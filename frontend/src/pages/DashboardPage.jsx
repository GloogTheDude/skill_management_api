import { useAuth } from "../auth/AuthContext";

export default function DashboardPage() {
  const { user } = useAuth();
  return (
    <section className="welcome-card">
      <p className="eyebrow">Accueil</p>
      <h1>Bonjour {user.first_name || ""}.</h1>
      <p>Votre espace est prêt. Utilisez la navigation pour commencer.</p>
    </section>
  );
}
