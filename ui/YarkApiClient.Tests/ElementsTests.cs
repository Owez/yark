using System.Text.Json;
using FluentAssertions;

namespace YarkApiClient.Tests;

public class ElementsTests
{
    [Fact]
    public void ElementsStringCycle()
    {
        Elements<string> basicStringTest = Elements<string>.NewTest("2024-01-02", "");
        string serializedString = JsonSerializer.Serialize(basicStringTest);
        serializedString.Should().Be("{\"2024-01-02T00:00:00\":\"\"}");
        Elements<string> basicDecodedString = JsonSerializer.Deserialize<Elements<string>>(serializedString);
        basicStringTest.Should().BeEquivalentTo(basicDecodedString);
    }

    [Fact]
    public void ElementsIntCycle()
    {
        Elements<int> basicIntTest = Elements<int>.NewTest("2024-01-02", 104203);
        string serializedInt = JsonSerializer.Serialize(basicIntTest);
        serializedInt.Should().Be("{\"2024-01-02T00:00:00\":104203}");
        Elements<int> basicDecodedInt = JsonSerializer.Deserialize<Elements<int>>(serializedInt);
        basicIntTest.Should().BeEquivalentTo(basicDecodedInt);
    }

    [Fact]
    public void ElementsBoolCycle()
    {
        Elements<bool> basicBooleanTest = Elements<bool>.NewTest("2024-01-02", false);
        string serializedBool = JsonSerializer.Serialize(basicBooleanTest);
        serializedBool.Should().Be("{\"2024-01-02T00:00:00\":false}");
        Elements<bool> basicDecodedBool = JsonSerializer.Deserialize<Elements<bool>>(serializedBool);
        basicBooleanTest.Should().BeEquivalentTo(basicDecodedBool);
    }

    [Fact]
    public void GetCurrentProperly()
    {
        Elements<string> someElements = new Elements<string>
        {
            { DateTime.Parse("2024-05-04"), "second one" },
            { DateTime.Parse("2024-07-01"), "third one" },
            { DateTime.Parse("2024-05-03"), "first one" }
        };
        someElements.Current().Should().Be("third one");
    }
}
