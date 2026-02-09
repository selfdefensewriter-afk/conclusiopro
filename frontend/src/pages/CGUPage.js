import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Scale, ArrowLeft, AlertTriangle, FileText } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';

const CGUPage = () => {
  const navigate = useNavigate();

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

      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center mb-12">
          <FileText className="h-16 w-16 text-primary mx-auto mb-4" strokeWidth={1.5} />
          <h1 className="font-serif text-4xl font-semibold text-primary mb-4">
            Conditions Générales d'Utilisation
          </h1>
          <p className="text-sm text-slate-500 font-sans">Dernière mise à jour : Février 2026</p>
        </div>

        <Alert className="mb-8 border-red-500 bg-red-50">
          <AlertTriangle className="h-5 w-5 text-red-600" />
          <AlertDescription className="font-sans text-sm text-red-700">
            <strong>Important :</strong> En utilisant ConclusioPro, vous acceptez pleinement ces conditions. 
            L'Application ne fournit AUCUN conseil juridique.
          </AlertDescription>
        </Alert>

        <div className="space-y-8">
          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">1. Objet des CGU</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>
                Les présentes Conditions Générales d'Utilisation ont pour objet de définir les modalités 
                d'accès et d'utilisation de l'application <strong>ConclusioPro</strong> (ci-après « l'Application »).
              </p>
              <p>
                L'Application propose un <strong>outil d'assistance pédagogique, rédactionnelle et formelle</strong>, 
                permettant aux utilisateurs de structurer, rédiger et mettre en forme leurs écrits, notamment judiciaires, 
                <strong className="text-red-600"> sans fournir de conseil juridique</strong>.
              </p>
            </CardContent>
          </Card>

          <Card className="border-red-200 bg-red-50 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-red-800 flex items-center gap-2">
                <AlertTriangle className="h-6 w-6" />
                2. Absence de conseil juridique – Clause fondamentale
              </CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-red-900 space-y-4">
              <p className="font-bold text-lg">⚠️ L'Application ne fournit aucun conseil juridique.</p>
              
              <p>Elle ne constitue en aucun cas :</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>une consultation juridique,</li>
                <li>une analyse juridique personnalisée,</li>
                <li>une assistance ou stratégie procédurale,</li>
                <li>une rédaction d'actes juridiques pour le compte de tiers.</li>
              </ul>

              <p className="font-bold">
                L'Application ne remplace pas un avocat ni aucun professionnel du droit.
              </p>

              <p className="font-bold">
                L'utilisateur reconnaît utiliser l'Application à ses seuls risques et périls.
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">3. Rôle de l'utilisateur</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>L'utilisateur :</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>rédige lui-même</strong> l'intégralité du contenu juridique ;</li>
                <li><strong>choisit librement</strong> les textes, arguments et formulations ;</li>
                <li><strong>demeure seul auteur et seul responsable</strong> des documents produits, modifiés ou exportés via l'Application.</li>
              </ul>
              <p className="font-bold text-primary mt-4">
                Aucune validation juridique n'est effectuée par l'éditeur.
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">4. Fonctionnalités proposées</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>L'Application permet notamment :</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>la structuration formelle de documents (plan, titres, numérotation) ;</li>
                <li>une assistance linguistique et rédactionnelle (clarification, reformulation) ;</li>
                <li>l'accès en consultation à des textes juridiques et décisions publiques ;</li>
                <li>la mise en page conforme aux usages judiciaires.</li>
              </ul>
              <div className="bg-amber-50 border border-amber-200 p-4 rounded-sm mt-4">
                <p className="font-semibold text-amber-800">
                  ⚠️ Les contenus juridiques accessibles sont fournis sans interprétation, hiérarchisation 
                  ou application automatisée à la situation de l'utilisateur.
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">5. Limitation de responsabilité</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>L'éditeur ne saurait être tenu responsable :</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>d'un rejet ou refus d'un document par une juridiction ;</li>
                <li>d'une erreur juridique, omission ou inadaptation du contenu ;</li>
                <li>des conséquences judiciaires, financières ou personnelles liées à l'utilisation de l'Application.</li>
              </ul>
              <p className="font-bold text-primary mt-4">
                La responsabilité de l'éditeur est strictement limitée aux fonctionnalités techniques de la plateforme.
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">6. Accès et disponibilité</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>
                L'Application est accessible sous réserve de disponibilité technique.
              </p>
              <p>
                L'éditeur se réserve le droit de suspendre, modifier ou interrompre tout ou partie des services, 
                sans préavis.
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">7. Propriété intellectuelle</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>
                L'Application, ses contenus, logiciels et interfaces sont protégés par le droit de la propriété intellectuelle.
              </p>
              <p className="font-bold text-primary">
                Les documents produits via l'Application restent la propriété exclusive de l'utilisateur.
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">8. Acceptation des CGU</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700">
              <p className="font-bold">
                L'utilisation de l'Application vaut acceptation pleine et entière des présentes CGU.
              </p>
            </CardContent>
          </Card>

          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">9. Droit applicable</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-700 space-y-3">
              <p>
                Les présentes CGU sont soumises au droit français.
              </p>
              <p>
                Tout litige relève de la compétence des juridictions françaises.
              </p>
            </CardContent>
          </Card>

          <div className="mt-12 p-8 bg-primary/5 border border-primary/20 rounded-sm">
            <h3 className="font-serif text-xl font-semibold text-primary mb-4 text-center">
              Résumé - Points essentiels
            </h3>
            <div className="font-sans text-slate-700 space-y-2">
              <p>✅ <strong>Vous rédigez vous-même</strong> - L'Application vous aide à structurer</p>
              <p>⚠️ <strong>Aucun conseil juridique</strong> - Ne remplace pas un avocat</p>
              <p>📝 <strong>Vous êtes seul responsable</strong> - Contenu et conséquences</p>
              <p>⚖️ <strong>Pas de garantie</strong> - Ni d'acceptation, ni de résultat</p>
              <p>🔒 <strong>Utilisation à vos risques</strong> - Relecture impérative recommandée</p>
            </div>
          </div>
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-slate-600 font-sans mb-4">
            Pour toute question sur ces CGU : legal@conclusiopro.com
          </p>
          <p className="text-xs text-slate-500 font-sans">
            Document juridique - Conservation recommandée
          </p>
        </div>
      </main>

      <footer className="border-t border-slate-200 py-8 px-6 mt-12">
        <div className="max-w-7xl mx-auto text-center text-slate-500 font-sans text-sm">
          <p>© 2026 ConclusioPro - Outil pédagogique d'aide à la rédaction juridique</p>
        </div>
      </footer>
    </div>
  );
};

export default CGUPage;