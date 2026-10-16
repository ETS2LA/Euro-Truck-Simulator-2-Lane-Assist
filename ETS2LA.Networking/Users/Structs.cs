namespace ETS2LA.Networking.Users;

public struct LoginResponse
{
    public string token { get; set; }
    public DateTime expiry { get; set; }
}

public struct RegisterResponse
{
    public string id { get; set; }
    public string authUrl { get; set; }
    public string authQrCode { get; set; }
    public string? error { get; set; }
}

public struct UserInfoResponse
{
    public string id { get; set; }
    public string username { get; set; }
    public UserRole role { get; set; }
    public PaddleCustomer? paddle { get; set; }
}