using System;
using System.Collections.Generic;
using HtmlAgilityPack;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Auth;
using Microsoft.WindowsAzure.Storage.Blob;
using System.Linq;
using static System.Configuration.ConfigurationManager;

namespace tocfcws
{
    public class Tocfcws
    {
        private static void Main(string[] args)
        {
            var urlAddress = AppSettings["url"];
            var listOfArticles = GetData(urlAddress);
            var salt = AppSettings["salt"];
            var containerReference = AppSettings["containerReference"];
            var accountName = AppSettings["accountName"];
            var accountKey = AppSettings["accountKey"];
            var consumerKey = AppSettings["consumerKey"];
            var consumerKeySecret = AppSettings["consumerKeySecret"];
            var accessToken = AppSettings["accessToken"];
            var accessTokenSecret = AppSettings["accessTokenSecret"];
            var truncateAmount = AppSettings["truncateAmount"];
            var twitter = new TwitterApi(consumerKey, consumerKeySecret, accessToken, accessTokenSecret);
            var account = new CloudStorageAccount(new StorageCredentials(accountName, accountKey), true);
            var blobClient = account.CreateCloudBlobClient();
            var container = blobClient.GetContainerReference(containerReference);
            container.CreateIfNotExists();

            foreach (var article in listOfArticles)
            {
                var combineTitleAndText = article.Title + ":- " + article.Text;
                var text = combineTitleAndText.Truncate(int.Parse(truncateAmount));
                var url = article.Link;
                var message = text + "... " + url;
                var hash = GetStringSha256Hash(salt + message);
                Console.WriteLine("hash :" + hash);
                CloudBlockBlob blob = container.GetBlockBlobReference(hash + ".txt");

                blob.GetSharedAccessSignature(new SharedAccessBlobPolicy()
                {
                    Permissions = SharedAccessBlobPermissions.Write | SharedAccessBlobPermissions.Delete,
                    SharedAccessExpiryTime =
                        DateTime.UtcNow.AddMinutes(
                            Convert.ToDouble(AppSettings["SharedAccessSignatureExpiryTimeOffset"]))
                });

                if (blob.Exists()) continue;
                Console.WriteLine(message + " " + hash);
                var response = twitter.Tweet("★: " + message);
                Console.WriteLine("★ :" + response.Result);
                blob.UploadText(message);
            }

            Console.WriteLine("---");

            DeleteOldBlobs(container);
        }

        private static void DeleteOldBlobs(CloudBlobContainer container)
        {
            var blobs = container.ListBlobs("", true).OfType<CloudBlockBlob>().Where(b =>
                b.Properties.LastModified != null &&
                (DateTime.UtcNow.AddDays(-35) > b.Properties.LastModified.Value.DateTime)).ToList();
            foreach (var blob in blobs)
            {
                blob.DeleteIfExists();
            }
        }

        private static IEnumerable<ArticleDto> GetData(string urlAddress)
        {
            var listOfArticles = new List<ArticleDto>();
            var web = new HtmlWeb();
            var doc = web.Load(urlAddress);
            var nodes = doc.DocumentNode.SelectNodes("//cfc-news-article-tile");

            foreach (var node in nodes)
            {
                if (!node.HasChildNodes) continue;
                var container = node.Element("a").ChildNodes["b"].ChildNodes["article"];
                var link  = "https://www.chelseafc.com" + node.Element("a").Attributes["href"].Value.Trim();
                var title = container.ChildNodes["div"].NextSibling.ChildNodes["h3"].InnerText.Trim();
                var text  = container.ChildNodes["div"].NextSibling.ChildNodes["p"].InnerText.Trim();
                var articleDto = new ArticleDto { Link = link, Text = text, Title = title };
                Console.WriteLine("Article found: " + title);
                listOfArticles.Add(articleDto);
            }

            return listOfArticles;
        }


        internal static string GetStringSha256Hash(string text)
        {
            if (string.IsNullOrEmpty(text))
                return string.Empty;

            using (var sha = new System.Security.Cryptography.SHA256Managed())
            {
                byte[] textData = System.Text.Encoding.UTF8.GetBytes(text);
                byte[] hash = sha.ComputeHash(textData);
                return BitConverter.ToString(hash).Replace("-", string.Empty);
            }
        }

    }


    public class ArticleDto
    {
        public string Title { get; set; }
        public string Link { get; set; }
        public string Text { get; set; }
    }

    public static class StringExt
    {
        public static string Truncate(this string value, int maxLength)
        {
            if (string.IsNullOrEmpty(value)) return value;
            return value.Length <= maxLength ? value : value.Substring(0, maxLength);
        }
    }
}
