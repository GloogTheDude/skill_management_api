import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError } from "../api/client";
import { useAuth } from "../auth/AuthContext";

export default function LoginPage() {
  const { login, authenticated, loading } = useAuth();
  const navigate = useNavigate();
  const [mail, setMail] = useState("");
  const [password, setPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (!loading && authenticated) {
    navigate("/app", { replace: true });
    return null;
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setSubmitting(true);
    setError("");
    try {
      await login(mail, password);
      navigate("/app", { replace: true });
    } catch (requestError) {
      if (requestError instanceof ApiError && requestError.status === 401) {
        setError("Adresse mail ou mot de passe incorrect.");
      } else {
        setError("Connexion impossible. Réessayez dans un instant.");
      }
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={handleSubmit}>
        <p className="eyebrow">Skill Management</p>
        <h1>Connexion</h1>
        <p className="muted">Connectez-vous pour accéder à votre espace.</p>
        {error && <div className="alert" role="alert">{error}</div>}
        <label htmlFor="mail">Adresse mail</label>
        <input id="mail" type="email" value={mail} onChange={(event) => setMail(event.target.value)} required autoComplete="username" />
        <label htmlFor="password">Mot de passe</label>
        <input id="password" type="password" value={password} onChange={(event) => setPassword(event.target.value)} required autoComplete="current-password" />
        <button className="button button-primary" type="submit" disabled={submitting}>
          {submitting ? "Connexion…" : "Se connecter"}
        </button>
      </form>
    </main>
  );
}
