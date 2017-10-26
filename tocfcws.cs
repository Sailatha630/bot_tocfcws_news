using System;
using System.Collections.Generic;
using HtmlAgilityPack;
using Microsoft.WindowsAzure.Storage;
using Microsoft.WindowsAzure.Storage.Auth;
using Microsoft.WindowsAzure.Storage.Blob;
using System.Configuration;

namespace scratch
{
    public class Tocfcws
    {
        private static void Main(string[] args)
        {
            const string urlAddress = @"http://www.chelseafc.com/news/latest-news.html";
            var listOfArticles = GetData(urlAddress);
            var salt = ConfigurationManager.AppSettings["salt"];
            var containerReference = ConfigurationManager.AppSettings["containerReference"];
            var accountName = ConfigurationManager.AppSettings["accountName"];
            var accountKey = ConfigurationManager.AppSettings["accountKey"];
            var consumerKey = ConfigurationManager.AppSettings["consumerKey"];
            var consumerKeySecret = ConfigurationManager.AppSettings["consumerKeySecret"];
            var accessToken = ConfigurationManager.AppSettings["accessToken"];
            var accessTokenSecret = ConfigurationManager.AppSettings["accessTokenSecret"];
            var truncateAmount = ConfigurationManager.AppSettings["truncateAmount"];
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
                    SharedAccessExpiryTime = DateTime.UtcNow.AddMinutes(Convert.ToDouble(ConfigurationManager.AppSettings["SharedAccessSignatureExpiryTimeOffset"]))
                });

                if (blob.Exists()) continue;
                Console.WriteLine(message + " " + hash);
                var response = twitter.Tweet("tocfcws: " + message);
                Console.WriteLine("tweet :" + response.Result);
                blob.UploadText(message);
            }
            Console.WriteLine("---");
        }

        private static IEnumerable<ArticleDto> GetData(string urlAddress)
        {
            var listOfArticles = new List<ArticleDto>();
            var web = new HtmlWeb();
            var doc = web.Load(urlAddress);
            var nodes = doc.DocumentNode.SelectNodes("//article");
            foreach (var node in nodes)
            {
                if (!node.HasChildNodes) continue;
                var header = node.Element("a").ChildNodes["header"];
                var articleDto = new ArticleDto
                {
                    Link = "https://www.chelseafc.com" + node.Element("a").Attributes["href"].Value.Trim(),
                    Text = node.Element("a").ChildNodes["p"].InnerText.Trim(),
                    Title = header.ChildNodes["h3"].InnerText.Trim()
                };
                Console.WriteLine("Article found: " + header.ChildNodes["h3"].InnerText.Trim());
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
