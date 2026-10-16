using ETS2LA.Networking.Users;
using ETS2LA.Networking.Settings;

using System;
using System.Net.Http;
using System.Threading.Tasks;
using System.Text.Json;
using System.Reflection;

namespace ETS2LA.Networking.News;

public class UserApiClient
{
    JsonSerializerOptions jsonOptions = new JsonSerializerOptions
    {
        PropertyNameCaseInsensitive = true,
        Converters = { new System.Text.Json.Serialization.JsonStringEnumConverter() }
    };

    public async Task<UserInfoResponse?> GetUserInfo(User user)
    {
        try
        {
            var apiServer = NetworkingSettings.Current.CurrentApiServer;
            if (apiServer == null)
            {
                throw new InvalidOperationException("CurrentApiServer is not set.");
            }

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", user.JwtToken);
            var response = await httpClient.GetAsync($"{apiServer.Value.BaseUrl}/user");
            response.EnsureSuccessStatusCode();

            var jsonResponse = await response.Content.ReadAsStringAsync();
            UserInfoResponse? userInfoResponse = JsonSerializer.Deserialize<UserInfoResponse>(jsonResponse, jsonOptions);

            if (userInfoResponse == null)
            {
                throw new InvalidOperationException("Failed to deserialize user info response.");
            }

            return userInfoResponse;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"GetUserInfo failed for user: {user.Username}. Exception: {ex.Message}");
        }

        return null;
    }

    public async Task<RegisterResponse?> Register(string username)
    {
        try
        {
            var apiServer = NetworkingSettings.Current.CurrentApiServer;
            if (apiServer == null)
            {
                throw new InvalidOperationException("CurrentApiServer is not set.");
            }

            using var httpClient = new HttpClient();
            var payload = new { username };
            var content = new StringContent(JsonSerializer.Serialize(payload), System.Text.Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync($"{apiServer.Value.BaseUrl}/users/register", content);
            response.EnsureSuccessStatusCode();

            var jsonResponse = await response.Content.ReadAsStringAsync();
            RegisterResponse? registerResponse = JsonSerializer.Deserialize<RegisterResponse>(jsonResponse, jsonOptions);

            if (registerResponse == null)
            {
                throw new InvalidOperationException("Failed to deserialize register response.");
            }

            return registerResponse;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Registration failed for user: {username}. Exception: {ex.Message}");
            return new RegisterResponse { error = ex.Message };
        }
    }

    public async Task<User?> Login(string username, string otpcode)
    {
        try
        {
            var apiServer = NetworkingSettings.Current.CurrentApiServer;
            if (apiServer == null)
            {
                throw new InvalidOperationException("CurrentApiServer is not set.");
            }

            using var httpClient = new HttpClient();
            var payload = new
            {
                username = username,
                otpcode = otpcode
            };
            var content = new StringContent(JsonSerializer.Serialize(payload), System.Text.Encoding.UTF8, "application/json");
            var response = await httpClient.PostAsync($"{apiServer.Value.BaseUrl}/users/login", content);
            response.EnsureSuccessStatusCode();

            var jsonResponse = await response.Content.ReadAsStringAsync();
            LoginResponse? loginResponse = JsonSerializer.Deserialize<LoginResponse>(jsonResponse, jsonOptions);

            if (loginResponse == null || !loginResponse.HasValue)
            {
                throw new InvalidOperationException("Failed to deserialize login response.");
            }

            LoginResponse login = loginResponse.Value;
            if (string.IsNullOrEmpty(login.token))
            {
                throw new InvalidOperationException("Login failed: token is null or empty.");
            }
            if (login.expiry == DateTime.MinValue)
            {
                throw new InvalidOperationException("Login failed: expiry is not set.");
            }
            
            var userInfo = await GetUserInfo(new User { JwtToken = login.token });
            if (userInfo == null)
            {
                throw new InvalidOperationException("Failed to retrieve user info after login.");
            }

            User user = new User
            {
                Id = Guid.Parse(userInfo.Value.id),
                Username = userInfo.Value.username,
                JwtToken = login.token,
                Expiry = login.expiry,
                Role = userInfo.Value.role,
                Paddle = userInfo.Value.paddle
            };

            return user;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Login failed for user: {username}. Exception: {ex.Message}");
        }

        return null;
    }

    public async Task<bool> Logout(User user)
    {
        try
        {
            var apiServer = NetworkingSettings.Current.CurrentApiServer;
            if (apiServer == null)
            {
                throw new InvalidOperationException("CurrentApiServer is not set.");
            }

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", user.JwtToken);
            var response = await httpClient.PostAsync($"{apiServer.Value.BaseUrl}/users/logout", null);
            response.EnsureSuccessStatusCode();

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Logout failed for user: {user.Username}. Exception: {ex.Message}");
        }

        return false;
    }

    public async Task<bool> RemoveAccount(User user)
    {
        try
        {
            var apiServer = NetworkingSettings.Current.CurrentApiServer;
            if (apiServer == null)
            {
                throw new InvalidOperationException("CurrentApiServer is not set.");
            }

            using var httpClient = new HttpClient();
            httpClient.DefaultRequestHeaders.Authorization = new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", user.JwtToken);
            var response = await httpClient.PostAsync($"{apiServer.Value.BaseUrl}/users/remove", null);
            response.EnsureSuccessStatusCode();

            return true;
        }
        catch (Exception ex)
        {
            Console.WriteLine($"Remove account failed for user: {user.Username}. Exception: {ex.Message}");
        }

        return false;
    }
}