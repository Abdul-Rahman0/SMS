import Link from 'next/link'; // Assuming Next.js, adjust imports as needed
// ... other imports

function Navbar() {
  // Assume you get the user state here, e.g., from a context, hook, or prop
  const user = useAuth(); // Replace useAuth() with your actual auth state hook/method

  return (
    <nav>
      {/* ... other navbar elements (logo, home link, etc.) */}

      <div>
        {user ? (
          // If user is logged in
          <>
            <Link href="/profile">Profile</Link>
            {/* You might also include a Logout button/link here or within the profile page */}
            {/* <button onClick={handleLogout}>Logout</button> */}
          </>
        ) : (
          // If user is not logged in
          <>
            <Link href="/login">Login</Link>
            <Link href="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar; 