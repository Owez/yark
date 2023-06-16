using System;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;

public class Article
{
    public int Id { get; set; }
    public string Title { get; set; }
    public string Content { get; set; }
    public DateTime PublishedDate { get; set; }

    public static async Task<Article> New(string title, string content)
    {
        using (HttpClient client = new HttpClient())
        {
            Article newArticle = new Article
            {
                Title = title,
                Content = content,
                PublishedDate = DateTime.Now
            };

            string articleJson = JsonSerializer.Serialize(newArticle);
            client.DefaultRequestHeaders.Accept.Add(new MediaTypeWithQualityHeaderValue("application/json"));

            HttpResponseMessage response = await client.PostAsync("https://api.example.com/article", new StringContent(articleJson, Encoding.UTF8, "application/json"));

            if (response.IsSuccessStatusCode)
            {
                string responseJson = await response.Content.ReadAsStringAsync();
                Article createdArticle = JsonSerializer.Deserialize<Article>(responseJson);
                return createdArticle;
            }
            else
            {
                Console.WriteLine($"Request failed: {response.StatusCode} - {response.ReasonPhrase}");
                return null;
            }
        }
    }
}

public class Program
{
    static async Task Main()
    {
        string title = "Sample Article";
        string content = "This is the content of the article.";

        Article createdArticle = await Article.New(title, content);

        if (createdArticle != null)
        {
            Console.WriteLine($"Article ID: {createdArticle.Id}");
            Console.WriteLine($"Title: {createdArticle.Title}");
            Console.WriteLine($"Content: {createdArticle.Content}");
            Console.WriteLine($"Published Date: {createdArticle.PublishedDate}");
        }
    }
}
