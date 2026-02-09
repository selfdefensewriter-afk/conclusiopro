import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../components/ui/accordion';
import { Scale, ArrowLeft, AlertTriangle, HelpCircle } from 'lucide-react';
import { Alert, AlertDescription } from '../components/ui/alert';

const FAQPage = () => {
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
          <HelpCircle className="h-16 w-16 text-primary mx-auto mb-4" strokeWidth={1.5} />
          <h1 className="font-serif text-4xl font-semibold text-primary mb-4">
            Questions Fréquentes
          </h1>
          <p className="text-lg text-slate-600 font-sans">
            Tout ce que vous devez savoir sur ConclusioPro
          </p>
        </div>

        <Alert className="mb-8 border-amber-500 bg-amber-50">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <AlertDescription className="font-sans text-sm">
            <strong>Rappel :</strong> Outil pédagogique - Ne fournit aucun conseil juridique - Ne remplace pas un avocat
          </AlertDescription>
        </Alert>

        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-serif text-2xl">L'application remplace-t-elle un avocat ?</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-600">
              <strong>Non.</strong> Elle aide uniquement à structurer et rédiger, sans analyse juridique personnalisée.
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="font-serif text-2xl">Qui est responsable du contenu final ?</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-slate-600">
              <strong>Vous uniquement.</strong> Vous rédigez, validez et assumez les conséquences.
            </CardContent>
          </Card>

          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-red-800">Quand consulter un avocat ?</CardTitle>
            </CardHeader>
            <CardContent className="font-sans text-red-700">
              <strong>Toujours en cas de doute.</strong> Surtout si: affaire complexe, enjeux importants, urgence, incompréhension.
            </CardContent>
          </Card>
        </div>

        <div className="mt-12 text-center text-sm text-slate-600 font-sans">
          Pour la FAQ complète, consultez la documentation ou contactez support@conclusiopro.com
        </div>
      </main>
    </div>
  );
};

export default FAQPage;