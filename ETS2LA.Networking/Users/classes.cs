namespace ETS2LA.Networking.Users;

[Serializable]
public enum UserRole
{
    User,
    Admin
}

[Serializable]
public class User
{
    public Guid Id { get; set; } = Guid.Empty;
    public string Username { get; set; } = "Anonymous";
    public string JwtToken { get; set; } = string.Empty;
    public DateTime Expiry { get; set; } = DateTime.MinValue;

    // This is essentially never changed, but for future proofing I'll leave it here.
    public UserRole Role { get; set; } = UserRole.User;
}