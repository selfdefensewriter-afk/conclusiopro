import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Scale, ArrowLeft, ArrowRight, Loader2, AlertTriangle } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const NewConclusion = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [templates, setTemplates] = useState([]);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const [formData, setFormData] = useState({
    type: '',
    parties: {
      demandeur: '',
      defendeur: '',
      tribunal: '',
      numeroRG: ''
    },
    faits: '',
    demandes: ''
  });

  const handleTypeSelect = (type) => {
    setFormData({ ...formData, type });
    fetchTemplates(type);
    setStep(2);
  };

  const fetchTemplates = async (type) => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/templates?type=${type}`, {
        withCredentials: true
      });
      setTemplates(response.data);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const handleTemplateSelect = (template) => {
    setSelectedTemplate(template);
    setFormData({
      ...formData,
      faits: template.faits_template,
      demandes: template.demandes_template
    });
    toast.success(`Template "${template.name}" appliqué`);
  };

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData({
        ...formData,
        [parent]: {
          ...formData[parent],
          [child]: value
        }
      });
    } else {
      setFormData({ ...formData, [field]: value });
    }
  };

  const handleGenerate = async () => {
    if (!formData.faits.trim() || !formData.demandes.trim()) {
      toast.error('Veuillez remplir les faits et les demandes');
      return;
    }

    setGenerating(true);

    try {
      const generateResponse = await axios.post(
        `${BACKEND_URL}/api/generate/conclusion`,
        formData,
        { withCredentials: true }
      );

      const conclusionText = generateResponse.data.conclusion_text;

      const createResponse = await axios.post(
        `${BACKEND_URL}/api/conclusions`,
        {
          ...formData,
          conclusion_text: conclusionText
        },
        { withCredentials: true }
      );

      toast.success('Conclusion générée avec succès! 1 crédit utilisé.');
      
      setTimeout(() => {
        navigate(`/conclusion/${createResponse.data.conclusion_id}`);
      }, 100);
    } catch (error) {
      console.error('Error generating conclusion:', error);
      
      if (error.response?.status === 403) {
        toast.error('Crédits insuffisants. Veuillez acheter des crédits.');
        setTimeout(() => {
          navigate('/tarifs');
        }, 2000);
      } else {
        toast.error('Erreur lors de la génération de la conclusion');
        setGenerating(false);
      }
    }
  };

  const renderStepIndicator = () => {
    const steps = [
      { num: 1, label: 'Type' },
      { num: 2, label: 'Parties' },
      { num: 3, label: 'Faits' },
      { num: 4, label: 'Demandes' }
    ];

    return (
      <div className="mb-12">
        <div className="flex items-center justify-center space-x-8">
          {steps.map((s, idx) => (
            <React.Fragment key={s.num}>
              <div className="flex flex-col items-center">
                <div
                  className={`h-10 w-10 rounded-full flex items-center justify-center font-sans font-medium ${
                    step >= s.num
                      ? 'bg-primary text-white'
                      : 'bg-slate-200 text-slate-500'
                  } transition-colors duration-200`}
                >
                  {s.num}
                </div>
                <span className="text-xs font-sans text-slate-600 mt-2">{s.label}</span>
              </div>
              {idx < steps.length - 1 && (
                <div
                  className={`h-0.5 w-16 ${
                    step > s.num ? 'bg-primary' : 'bg-slate-200'
                  } transition-colors duration-200`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              onClick={() => navigate('/dashboard')}
              variant="ghost"
              className="h-10 px-3 rounded-sm"
              data-testid="back-to-dashboard-btn"
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
        <Alert className="mb-8 border-amber-500 bg-amber-50">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <AlertDescription className="font-sans text-sm text-slate-700">
            <strong>Important :</strong> Outil pédagogique d'aide à la structuration. Ne fournit aucun conseil juridique. Ne remplace pas un avocat.
          </AlertDescription>
        </Alert>

        <h1 className="font-serif text-4xl font-semibold text-primary mb-8 text-center">
          Nouveau document structuré
        </h1>

        {renderStepIndicator()}

        {step === 1 && (
          <div className="space-y-6">
            <Card
              className="border-slate-200 rounded-sm cursor-pointer card-hover"
              onClick={() => handleTypeSelect('jaf')}
              data-testid="type-jaf-card"
            >
              <CardHeader>
                <CardTitle className="font-serif text-2xl text-primary">
                  Juge aux Affaires Familiales (JAF)
                </CardTitle>
                <CardDescription className="font-sans text-base">
                  Pour les affaires de divorce, garde d'enfants, autorité parentale, pension alimentaire, etc.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card
              className="border-slate-200 rounded-sm cursor-pointer card-hover"
              onClick={() => handleTypeSelect('penal')}
              data-testid="type-penal-card"
            >
              <CardHeader>
                <CardTitle className="font-serif text-2xl text-primary">Affaire Pénale</CardTitle>
                <CardDescription className="font-sans text-base">
                  Pour les affaires pénales nécessitant des conclusions en défense ou en partie civile.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            {templates.length > 0 && (
              <Card className="border-amber-200 bg-amber-50 rounded-sm">
                <CardHeader>
                  <CardTitle className="font-serif text-xl text-primary flex items-center">
                    💡 Templates disponibles
                  </CardTitle>
                  <CardDescription className="font-sans">
                    Sélectionnez un template pour pré-remplir le formulaire avec un modèle adapté
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid gap-3">
                    {templates.map((template) => (
                      <button
                        key={template.template_id}
                        onClick={() => handleTemplateSelect(template)}
                        className={`p-4 border rounded-sm text-left transition-all duration-200 ${
                          selectedTemplate?.template_id === template.template_id
                            ? 'border-accent bg-accent/5 shadow-sm'
                            : 'border-slate-200 hover:border-accent/50 hover:bg-slate-50'
                        }`}
                        data-testid={`template-${template.template_id}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <h4 className="font-sans font-semibold text-sm text-primary mb-1">
                              {template.name}
                            </h4>
                            <p className="text-xs text-slate-600 font-sans mb-2">
                              {template.description}
                            </p>
                            <span className="inline-block text-xs px-2 py-1 bg-slate-100 text-slate-600 rounded-sm">
                              {template.category}
                            </span>
                          </div>
                          {selectedTemplate?.template_id === template.template_id && (
                            <span className="text-accent text-sm font-sans">✓ Sélectionné</span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">Informations sur les parties</CardTitle>
              <CardDescription className="font-sans">
                Renseignez les informations relatives aux parties et à la juridiction
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="tribunal" className="font-sans font-medium">
                  Tribunal compétent
                </Label>
                <Input
                  id="tribunal"
                  value={formData.parties.tribunal}
                  onChange={(e) => handleInputChange('parties.tribunal', e.target.value)}
                  placeholder="Ex: Tribunal Judiciaire de Paris"
                  className="h-12 rounded-sm border-slate-200 font-sans"
                  data-testid="input-tribunal"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="numeroRG" className="font-sans font-medium">
                  Numéro RG / Parquet
                </Label>
                <Input
                  id="numeroRG"
                  value={formData.parties.numeroRG}
                  onChange={(e) => handleInputChange('parties.numeroRG', e.target.value)}
                  placeholder="Ex: 23/12345"
                  className="h-12 rounded-sm border-slate-200 font-sans"
                  data-testid="input-numero-rg"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="demandeur" className="font-sans font-medium">
                  Demandeur / Partie civile
                </Label>
                <Input
                  id="demandeur"
                  value={formData.parties.demandeur}
                  onChange={(e) => handleInputChange('parties.demandeur', e.target.value)}
                  placeholder="Nom et prénom du demandeur"
                  className="h-12 rounded-sm border-slate-200 font-sans"
                  data-testid="input-demandeur"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="defendeur" className="font-sans font-medium">
                  Défendeur / Prévenu
                </Label>
                <Input
                  id="defendeur"
                  value={formData.parties.defendeur}
                  onChange={(e) => handleInputChange('parties.defendeur', e.target.value)}
                  placeholder="Nom et prénom du défendeur"
                  className="h-12 rounded-sm border-slate-200 font-sans"
                  data-testid="input-defendeur"
                />
              </div>

              <div className="flex justify-between pt-6">
                <Button
                  onClick={() => setStep(1)}
                  variant="outline"
                  className="h-12 px-6 rounded-sm border-slate-300 font-sans"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Retour
                </Button>
                <Button
                  onClick={() => setStep(3)}
                  className="bg-primary hover:bg-primary/90 text-white h-12 px-6 rounded-sm font-sans"
                  data-testid="next-to-faits-btn"
                >
                  Suivant
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
          </div>
        )}

        {step === 3 && (
          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">Exposé des faits</CardTitle>
              <CardDescription className="font-sans">
                Décrivez de manière chronologique et objective les faits de l'affaire
                {selectedTemplate && (
                  <span className="block mt-2 text-accent text-sm">
                    ✓ Template "{selectedTemplate.name}" appliqué - vous pouvez modifier le texte
                  </span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="faits" className="font-sans font-medium">
                  Faits
                </Label>
                <Textarea
                  id="faits"
                  value={formData.faits}
                  onChange={(e) => handleInputChange('faits', e.target.value)}
                  placeholder="Décrivez les faits importants de manière chronologique..."
                  className="min-h-[300px] rounded-sm border-slate-200 font-sans"
                  data-testid="textarea-faits"
                />
              </div>

              <div className="flex justify-between pt-6">
                <Button
                  onClick={() => setStep(2)}
                  variant="outline"
                  className="h-12 px-6 rounded-sm border-slate-300 font-sans"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Retour
                </Button>
                <Button
                  onClick={() => setStep(4)}
                  className="bg-primary hover:bg-primary/90 text-white h-12 px-6 rounded-sm font-sans"
                  data-testid="next-to-demandes-btn"
                >
                  Suivant
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {step === 4 && (
          <Card className="border-slate-200 rounded-sm">
            <CardHeader>
              <CardTitle className="font-serif text-2xl text-primary">Vos demandes</CardTitle>
              <CardDescription className="font-sans">
                Précisez ce que vous demandez au tribunal
                {selectedTemplate && (
                  <span className="block mt-2 text-accent text-sm">
                    ✓ Template "{selectedTemplate.name}" appliqué - vous pouvez modifier le texte
                  </span>
                )}
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="demandes" className="font-sans font-medium">
                  Demandes
                </Label>
                <Textarea
                  id="demandes"
                  value={formData.demandes}
                  onChange={(e) => handleInputChange('demandes', e.target.value)}
                  placeholder="Listez vos demandes précises au tribunal...\n\nExemple:\n- Fixer la résidence de l'enfant chez le demandeur\n- Établir un droit de visite et d'hébergement\n- Fixer une pension alimentaire"
                  className="min-h-[300px] rounded-sm border-slate-200 font-sans"
                  data-testid="textarea-demandes"
                />
              </div>

              <div className="flex justify-between pt-6">
                <Button
                  onClick={() => setStep(3)}
                  variant="outline"
                  className="h-12 px-6 rounded-sm border-slate-300 font-sans"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Retour
                </Button>
                <Button
                  onClick={handleGenerate}
                  disabled={generating}
                  className="bg-accent hover:bg-accent/90 text-white h-12 px-8 rounded-sm font-sans font-medium"
                  data-testid="generate-conclusion-btn"
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Génération en cours...
                    </>
                  ) : (
                    'Générer la conclusion'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default NewConclusion;