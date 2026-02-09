import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Scale, FileText, Book, Shield, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';

const LandingPage = () => {
  const navigate = useNavigate();

  const handleLogin = () => {
    // Redirect to backend Google OAuth endpoint
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    window.location.href = `${backendUrl}/api/auth/google/login`;
  };

  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Scale className="h-8 w-8 text-primary" strokeWidth={1.5} />
            <span className="font-serif text-2xl font-semibold text-primary">ConclusioPro</span>
          </div>
          <div className="flex items-center gap-4">
            <Button
              onClick={() => navigate('/tarifs')}
              variant="ghost"
              className="font-sans"
            >
              Tarifs
            </Button>
            <Button 
              onClick={handleLogin}
              className="bg-primary hover:bg-primary/90 text-white h-12 px-6 rounded-sm font-sans font-medium"
              data-testid="header-login-btn"
            >
              Connexion / Inscription
            </Button>
          </div>
        </div>
      </nav>

      <Alert className="max-w-7xl mx-auto my-6 border-amber-500 bg-amber-50">
        <AlertTriangle className="h-5 w-5 text-amber-600" />
        <AlertDescription className="font-sans text-sm text-slate-700">
          <strong>Important :</strong> ConclusioPro est un outil pédagogique d'aide à la rédaction. 
          Il ne fournit aucun conseil juridique et ne remplace pas un avocat.
        </AlertDescription>
      </Alert>

      <section className="hero-section py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-8">
              <h1 className="font-serif text-5xl lg:text-6xl font-semibold text-primary tracking-tight leading-tight">
                Apprenez à structurer vos écritures juridiques
              </h1>
              <p className="text-lg text-slate-600 font-sans leading-relaxed">
                Outil pédagogique pour particuliers : modèles de structure, aide à la rédaction, 
                mise en page conforme aux usages du barreau. Vous gardez le contrôle total de votre contenu.
              </p>
              <div className="flex gap-4">
                <Button 
                  onClick={handleLogin}
                  size="lg"
                  className="bg-primary hover:bg-primary/90 text-white h-14 px-8 rounded-sm font-sans font-medium text-base"
                  data-testid="hero-get-started-btn"
                >
                  Commencer l'apprentissage
                </Button>
                <Button 
                  variant="outline"
                  size="lg"
                  className="h-14 px-8 rounded-sm font-sans font-medium text-base border-slate-300"
                  onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
                >
                  En savoir plus
                </Button>
              </div>
              <p className="text-sm text-slate-500 font-sans flex items-center gap-2">
                <span className="inline-flex items-center justify-center w-5 h-5 rounded-full bg-green-100 text-green-600 text-xs">✓</span>
                Outil pédagogique • Aucun conseil juridique • Vous rédigez vous-même
              </p>
            </div>
            <div className="hidden lg:block">
              <img 
                src="https://images.unsplash.com/photo-1564846824194-346b7871b855" 
                alt="Rédaction juridique"
                className="rounded-sm shadow-lg w-full"
              />
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="py-24 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif text-4xl font-semibold text-primary mb-4">Fonctionnalités pédagogiques</h2>
            <p className="text-lg text-slate-600 font-sans">Apprenez à rédiger par vous-même avec nos outils d'assistance</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="p-8 border border-slate-200 rounded-sm card-hover bg-white" data-testid="feature-card-structure">
              <div className="h-12 w-12 bg-slate-100 rounded-sm flex items-center justify-center mb-6">
                <FileText className="h-6 w-6 text-primary" strokeWidth={1.5} />
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary mb-3">Modèles de structure</h3>
              <p className="text-slate-600 font-sans leading-relaxed">
                Apprenez la structure standard des écritures juridiques : en-tête, faits, discussion, demandes.
              </p>
            </div>

            <div className="p-8 border border-slate-200 rounded-sm card-hover bg-white" data-testid="feature-card-code">
              <div className="h-12 w-12 bg-slate-100 rounded-sm flex items-center justify-center mb-6">
                <Book className="h-6 w-6 text-primary" strokeWidth={1.5} />
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary mb-3">Base documentaire</h3>
              <p className="text-slate-600 font-sans leading-relaxed">
                Consultez les articles du Code Civil souvent cités dans les affaires similaires (non interprété).
              </p>
            </div>

            <div className="p-8 border border-slate-200 rounded-sm card-hover bg-white" data-testid="feature-card-editor">
              <div className="h-12 w-12 bg-slate-100 rounded-sm flex items-center justify-center mb-6">
                <Shield className="h-6 w-6 text-primary" strokeWidth={1.5} />
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary mb-3">Assistant linguistique</h3>
              <p className="text-slate-600 font-sans leading-relaxed">
                Amélioration de la clarté, du vocabulaire et du ton. Pas de conseil juridique, juste de la rédaction.
              </p>
            </div>

            <div className="p-8 border border-slate-200 rounded-sm card-hover bg-white" data-testid="feature-card-export">
              <div className="h-12 w-12 bg-slate-100 rounded-sm flex items-center justify-center mb-6">
                <Scale className="h-6 w-6 text-primary" strokeWidth={1.5} />
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary mb-3">Mise en page conforme</h3>
              <p className="text-slate-600 font-sans leading-relaxed">
                Formatage automatique selon les usages : police, marges, numérotation. Pure mise en forme.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-slate-50">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="font-serif text-4xl font-semibold text-primary">Pour qui ?</h2>
          <p className="text-lg text-slate-600 font-sans leading-relaxed">
            ConclusioPro s'adresse aux <strong>particuliers</strong> qui se défendent seuls (affaires familiales JAF ou pénales) 
            et qui ont besoin d'aide pour <strong>structurer et rédiger</strong> leurs écrits. Nous ne rédigeons pas à votre place : 
            nous vous aidons à mieux écrire vous-même.
          </p>
          <div className="bg-red-50 border border-red-200 p-6 rounded-sm text-left">
            <h3 className="font-sans font-semibold text-red-800 mb-3 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Avertissement légal important
            </h3>
            <ul className="space-y-2 text-sm text-red-700 font-sans">
              <li>• Cet outil ne fournit AUCUN conseil juridique personnalisé</li>
              <li>• Il ne remplace PAS un avocat</li>
              <li>• Vous rédigez vous-même votre document</li>
              <li>• Nous fournissons uniquement : structure, aide rédactionnelle, mise en forme</li>
              <li>• En cas de doute, consultez un professionnel du droit</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-white">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="font-serif text-4xl font-semibold text-primary mb-4">Comment ça marche ?</h2>
            <p className="text-lg text-slate-600 font-sans">Processus d'apprentissage en 3 étapes</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-serif font-bold text-accent">1</span>
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary">Choisissez un modèle</h3>
              <p className="text-slate-600 font-sans">
                Sélectionnez le type d'affaire et explorez nos modèles pédagogiques de structure.
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-serif font-bold text-accent">2</span>
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary">Rédigez avec assistance</h3>
              <p className="text-slate-600 font-sans">
                Utilisez nos outils d'aide à la rédaction pour améliorer clarté et structure. Vous écrivez.
              </p>
            </div>

            <div className="text-center space-y-4">
              <div className="w-16 h-16 bg-accent/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl font-serif font-bold text-accent">3</span>
              </div>
              <h3 className="font-serif text-xl font-semibold text-primary">Exportez en PDF</h3>
              <p className="text-slate-600 font-sans">
                Obtenez un document bien formaté, conforme aux usages en termes de présentation.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 px-6 bg-white">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <h2 className="font-serif text-4xl font-semibold text-primary mb-8">Prêt à commencer ?</h2>
          <p className="text-lg text-slate-600 font-sans mb-8">
            Commencez à apprendre la rédaction d'écrits juridiques structurés.
          </p>
          <div className="space-y-4">
            <Button 
              onClick={handleLogin}
              size="lg"
              className="bg-accent hover:bg-accent/90 text-white h-14 px-12 rounded-sm font-sans font-medium text-base"
              data-testid="cta-get-started-btn"
            >
              Créer mon compte gratuit
            </Button>
            <p className="text-sm text-slate-500 font-sans">
              🔒 Connexion sécurisée • 📝 Outil pédagogique • ⚖️ Vous rédigez vous-même
            </p>
          </div>
        </div>
      </section>

      <footer className="border-t border-slate-200 py-8 px-6">
        <div className="max-w-7xl mx-auto text-center text-slate-500 font-sans text-sm space-y-2">
          <p>© 2026 ConclusioPro - Outil pédagogique d'aide à la rédaction juridique</p>
          <p className="text-xs font-semibold text-red-600">
            NE FOURNIT AUCUN CONSEIL JURIDIQUE - NE REMPLACE PAS UN AVOCAT
          </p>
          <p className="text-xs">Vous rédigez vous-même vos documents. Nous fournissons uniquement structure, aide linguistique et mise en forme.</p>
          <div className="mt-4 pt-4 border-t border-slate-200 flex justify-center gap-6">
            <button 
              onClick={() => navigate('/faq')}
              className="text-primary hover:underline font-medium"
            >
              Questions Fréquentes (FAQ)
            </button>
            <span className="text-slate-300">•</span>
            <button 
              onClick={() => navigate('/cgu')}
              className="text-primary hover:underline font-medium"
            >
              Conditions Générales d'Utilisation
            </button>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;