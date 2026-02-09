import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Scale, ArrowLeft, Check, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';

const PricingPage = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);

  const handlePurchase = async () => {
    setLoading(true);
    
    try {
      const originUrl = window.location.origin;
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/payments/create-checkout`,
        {
          package_id: 'essentielle',
          origin_url: originUrl
        },
        { withCredentials: true }
      );

      window.location.href = response.data.url;
    } catch (error) {
      console.error('Payment error:', error);
      if (error.response?.status === 401) {
        // User not logged in - redirect to Google OAuth
        const backendUrl = process.env.REACT_APP_BACKEND_URL;
        window.location.href = `${backendUrl}/api/auth/google/login`;
      } else {
        alert('Erreur lors de la création du paiement. Veuillez réessayer.');
        setLoading(false);
      }
    }
  };

  const handleGetStarted = () => {
    const backendUrl = process.env.REACT_APP_BACKEND_URL;
    window.location.href = `${backendUrl}/api/auth/google/login`;
  };

  const plans = [
    {
      name: "Offre Essentielle",
      subtitle: "Rédaction autonome",
      price: "29",
      period: "par document",
      description: "Tout ce dont vous avez besoin pour rédiger vos écrits juridiques de manière structurée et professionnelle.",
      features: [
        "Accès à l'outil de rédaction guidée",
        "Structuration complète des documents",
        "9 templates pédagogiques (JAF + Pénal)",
        "Base Code Civil intégrée",
        "Assistance linguistique IA (Gemini 3 Flash)",
        "Éditeur de texte riche",
        "Recherche et insertion d'articles",
        "Mise en forme conforme aux usages judiciaires",
        "Export PDF professionnel",
        "Sauvegarde et historique illimités"
      ],
      cta: "Commencer maintenant",
      ideal: "Idéal pour les justiciables qui savent ce qu'ils veulent dire mais ne savent pas comment l'écrire de manière structurée."
    }
  ];

  const comingSoon = [
    {
      name: "Avancée",
      subtitle: "Rédaction + clarté",
      price: "49",
      status: "Prochainement"
    },
    {
      name: "Sérénité",
      subtitle: "Dossier complet",
      price: "89",
      status: "Prochainement"
    }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => navigate('/')}
              variant="ghost"
              className="h-10 px-3 rounded-sm"
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div className="flex items-center space-x-2">
              <Scale className="h-8 w-8 text-primary" strokeWidth={1.5} />
              <span className="font-serif text-2xl font-semibold text-primary">ConclusioPro</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <h1 className="font-serif text-5xl font-semibold text-primary mb-4">
            Tarifs transparents
          </h1>
          <p className="text-xl text-slate-600 font-sans mb-6">
            Choisissez l'offre adaptée à votre besoin
          </p>
          <p className="text-base text-slate-600 font-sans max-w-3xl mx-auto">
            Vous ne payez pas pour du droit. Vous payez pour <strong>écrire clairement, proprement et efficacement</strong>, 
            quand vous avez choisi de vous défendre seul.
          </p>
        </div>

        <Alert className="mb-12 max-w-4xl mx-auto border-amber-500 bg-amber-50">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <AlertDescription className="font-sans text-sm">
            <strong>Important :</strong> Cette plateforme est un outil de rédaction procédurale. 
            Elle ne fournit aucun conseil juridique et ne remplace pas un avocat.
          </AlertDescription>
        </Alert>

        <div className="max-w-4xl mx-auto mb-16">
          <Card className="border-accent border-2 rounded-sm shadow-lg">
            <CardHeader className="text-center pb-8">
              <CardTitle className="font-serif text-3xl text-primary mb-2">
                {plans[0].name}
              </CardTitle>
              <CardDescription className="font-sans text-slate-600 text-lg mb-4">
                {plans[0].subtitle}
              </CardDescription>
              <div className="mt-6">
                <span className="font-serif text-6xl font-bold text-primary">{plans[0].price}€</span>
                <span className="text-slate-500 font-sans text-lg">/{plans[0].period}</span>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-sm">
                <p className="text-sm text-slate-700 font-sans text-center">
                  {plans[0].ideal}
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                {plans[0].features.map((feature, idx) => (
                  <div key={idx} className="flex items-start gap-3">
                    <Check className="h-5 w-5 text-accent flex-shrink-0 mt-0.5" />
                    <span className="text-sm font-sans text-slate-700">{feature}</span>
                  </div>
                ))}
              </div>

              <div className="pt-6">
                <Button
                  onClick={handlePurchase}
                  disabled={loading}
                  className="w-full h-14 bg-accent hover:bg-accent/90 text-white rounded-sm font-sans font-medium text-lg"
                  data-testid="purchase-btn"
                >
                  {loading ? 'Redirection vers le paiement...' : plans[0].cta}
                </Button>
                <p className="text-xs text-center text-red-600 font-sans font-semibold pt-3">
                  ⚠️ Cette plateforme ne fournit aucun conseil juridique
                </p>
              </div>
            </CardContent>
          </Card>

          <div className="mt-12">
            <h3 className="font-serif text-2xl font-semibold text-primary text-center mb-6">
              Offres à venir
            </h3>
            <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
              {comingSoon.map((plan) => (
                <Card key={plan.name} className="border-slate-200 rounded-sm opacity-75">
                  <CardHeader className="text-center">
                    <div className="inline-block bg-slate-100 text-slate-600 px-3 py-1 rounded-full text-xs font-sans font-medium mb-3">
                      {plan.status}
                    </div>
                    <CardTitle className="font-serif text-xl text-slate-600">{plan.name}</CardTitle>
                    <CardDescription className="font-sans text-slate-500">
                      {plan.subtitle}
                    </CardDescription>
                    <div className="mt-4">
                      <span className="font-serif text-3xl font-bold text-slate-400">{plan.price}€</span>
                      <span className="text-slate-400 font-sans">/document</span>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </div>

        <div className="max-w-5xl mx-auto mb-16">
          <h2 className="font-serif text-3xl font-semibold text-primary text-center mb-8">
            Comprendre la différence
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            <Card className="border-slate-200 rounded-sm">
              <CardHeader>
                <CardTitle className="font-serif text-xl text-primary">
                  Conclusions par un avocat
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="font-sans text-slate-600">Tarif</span>
                  <span className="font-sans font-bold text-lg">600€ à 1 200€</span>
                </div>
                <div className="space-y-2 text-sm font-sans text-slate-700">
                  <p>✓ Conseil juridique personnalisé</p>
                  <p>✓ Stratégie procédurale</p>
                  <p>✓ Représentation possible</p>
                  <p>✓ Responsabilité professionnelle</p>
                </div>
                <p className="text-xs text-slate-500 font-sans italic pt-2">
                  Service juridique complet et professionnel
                </p>
              </CardContent>
            </Card>

            <Card className="border-accent border-2 rounded-sm bg-accent/5">
              <CardHeader>
                <CardTitle className="font-serif text-xl text-primary">
                  Notre solution ConclusioPro
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="font-sans text-slate-600">À partir de</span>
                  <span className="font-sans font-bold text-lg text-accent">29€</span>
                </div>
                <div className="space-y-2 text-sm font-sans text-slate-700">
                  <p>✓ Outil de rédaction autonome</p>
                  <p>✓ Structuration et mise en forme</p>
                  <p>✓ Vous restez maître de votre dossier</p>
                  <p>⚠️ Aucun conseil juridique</p>
                </div>
                <p className="text-xs text-slate-500 font-sans italic pt-2">
                  Assistance rédactionnelle et formelle uniquement
                </p>
              </CardContent>
            </Card>
          </div>
          <p className="text-center text-lg font-sans text-slate-600 mt-8 font-medium">
            👉 Deux besoins différents. Deux réponses différentes.
          </p>
        </div>

        <div className="max-w-4xl mx-auto bg-primary/5 border border-primary/20 rounded-sm p-8 text-center">
          <h3 className="font-serif text-2xl font-semibold text-primary mb-4">
            Accessible quand on se défend seul
          </h3>
          <p className="font-sans text-slate-700 mb-6">
            ConclusioPro vous aide à <strong>gagner du temps</strong>, obtenir de la <strong>clarté</strong> 
            et une <strong>mise en forme professionnelle</strong> pour vos écrits judiciaires.
          </p>
          <div className="space-y-2 text-sm font-sans text-slate-600">
            <p>✓ Pas de promesse juridique</p>
            <p>✓ Pas de résultat garanti</p>
            <p>✓ Pas d'analyse de fond</p>
            <p className="font-bold text-primary pt-2">Prix = outil, pas prestation juridique</p>
          </div>
        </div>

        <div className="mt-16 text-center">
          <p className="text-sm text-slate-600 font-sans mb-4">
            Des questions sur nos offres ?
          </p>
          <div className="flex justify-center gap-6">
            <Button
              onClick={() => navigate('/faq')}
              variant="outline"
              className="rounded-sm border-slate-300"
            >
              Consulter la FAQ
            </Button>
            <Button
              onClick={() => navigate('/cgu')}
              variant="outline"
              className="rounded-sm border-slate-300"
            >
              Lire les CGU
            </Button>
          </div>
        </div>
      </main>

      <footer className="border-t border-slate-200 py-8 px-6 mt-12">
        <div className="max-w-7xl mx-auto text-center text-slate-500 font-sans text-sm">
          <p className="font-semibold text-red-600 mb-2">
            Cette plateforme est un outil de rédaction procédurale.<br/>
            Elle ne fournit aucun conseil juridique et ne remplace pas un avocat.
          </p>
          <p>© 2026 ConclusioPro - Outil pédagogique d'aide à la rédaction juridique</p>
        </div>
      </footer>
    </div>
  );
};

export default PricingPage;