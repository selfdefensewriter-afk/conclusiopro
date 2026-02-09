import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Underline_ from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Scale, ArrowLeft, Save, FileDown, Search, Loader2, Bold, Italic, Underline, List, ListOrdered, FileText } from 'lucide-react';
import { toast } from 'sonner';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '../components/ui/accordion';
import PiecesManager from '../components/PiecesManager';

// Tiptap editor styles
import '../styles/tiptap.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ConclusionEditor = () => {
  const { conclusionId } = useParams();
  const navigate = useNavigate();
  const [conclusion, setConclusion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [articles, setArticles] = useState([]);
  const [searchingArticles, setSearchingArticles] = useState(false);
  const [initialContent, setInitialContent] = useState('');
  const [pieces, setPieces] = useState([]);
  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Underline_,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      Placeholder.configure({
        placeholder: 'Commencez à rédiger votre conclusion...',
      }),
    ],
    content: initialContent,
    editorProps: {
      attributes: {
        class: 'prose prose-slate max-w-none min-h-[400px] p-4 focus:outline-none',
      },
    },
  });

  // Update editor content when initialContent changes
  useEffect(() => {
    if (editor && initialContent && !editor.isDestroyed) {
      editor.commands.setContent(initialContent);
    }
  }, [editor, initialContent]);

  useEffect(() => {
    fetchConclusion();
    fetchPieces();
  }, [conclusionId]);

  const fetchConclusion = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/conclusions/${conclusionId}`,
        { withCredentials: true }
      );
      setConclusion(response.data);
      setInitialContent(response.data.conclusion_text || '');
    } catch (error) {
      console.error('Error fetching conclusion:', error);
      toast.error('Erreur lors du chargement de la conclusion');
      navigate('/dashboard');
    } finally {
      setLoading(false);
    }
  };

  const fetchPieces = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/conclusions/${conclusionId}/pieces`,
        { withCredentials: true }
      );
      setPieces(response.data);
    } catch (error) {
      console.error('Error fetching pieces:', error);
    }
  };

  const handleInsertPieceReference = (piece) => {
    if (!editor) return;
    const reference = `(voir Pièce n°${piece.numero})`;
    editor.chain().focus().insertContent(reference).run();
    toast.success('Référence insérée');
  };

  const generateBordereauText = () => {
    if (pieces.length === 0) return '';
    
    let text = '<h2>BORDEREAU DE PIÈCES</h2>';
    text += '<ul>';
    pieces.forEach((piece) => {
      text += `<li><strong>Pièce n°${piece.numero}</strong> : ${piece.nom}`;
      if (piece.description) {
        text += ` - ${piece.description}`;
      }
      text += '</li>';
    });
    text += '</ul>';
    return text;
  };

  const handleInsertBordereau = () => {
    if (!editor || pieces.length === 0) {
      toast.error('Aucune pièce à lister');
      return;
    }
    
    const bordereauHtml = generateBordereauText();
    editor.chain().focus().insertContent(bordereauHtml).run();
    toast.success('Bordereau de pièces inséré');
  };

  const handleSave = async () => {
    if (!editor) return;
    setSaving(true);
    try {
      await axios.put(
        `${BACKEND_URL}/api/conclusions/${conclusionId}`,
        {
          conclusion_text: editor.getHTML(),
          status: 'completed'
        },
        { withCredentials: true }
      );
      toast.success('Conclusion sauvegardée');
    } catch (error) {
      console.error('Error saving conclusion:', error);
      toast.error('Erreur lors de la sauvegarde');
    } finally {
      setSaving(false);
    }
  };

  const handleExportPDF = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/conclusions/${conclusionId}/pdf`,
        {
          withCredentials: true,
          responseType: 'blob'
        }
      );
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `conclusion_${conclusionId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      toast.success('PDF exporté avec succès');
    } catch (error) {
      console.error('Error exporting PDF:', error);
      toast.error('Erreur lors de l\'export PDF');
    }
  };

  const handleSearchArticles = async () => {
    if (!searchQuery.trim()) {
      toast.error('Veuillez entrer un terme de recherche');
      return;
    }

    setSearchingArticles(true);
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/code-civil/search?q=${encodeURIComponent(searchQuery)}`,
        { withCredentials: true }
      );
      setArticles(response.data);
      if (response.data.length === 0) {
        toast.info('Aucun article trouvé');
      }
    } catch (error) {
      console.error('Error searching articles:', error);
      toast.error('Erreur lors de la recherche');
    } finally {
      setSearchingArticles(false);
    }
  };

  const insertArticle = (article) => {
    if (!editor) return;
    const articleText = `<p><strong>Article ${article.numero} - ${article.titre}:</strong></p><p>${article.contenu}</p>`;
    editor.chain().focus().insertContent(articleText).run();
    toast.success('Article inséré');
  };

  // Toolbar component for the editor
  const EditorToolbar = () => {
    if (!editor) return null;

    return (
      <div className="flex flex-wrap gap-1 p-2 border-b border-slate-200 bg-slate-50">
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleBold().run()}
          className={`h-8 w-8 p-0 ${editor.isActive('bold') ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-bold"
        >
          <Bold className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleItalic().run()}
          className={`h-8 w-8 p-0 ${editor.isActive('italic') ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-italic"
        >
          <Italic className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          className={`h-8 w-8 p-0 ${editor.isActive('underline') ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-underline"
        >
          <Underline className="h-4 w-4" />
        </Button>
        <div className="w-px h-8 bg-slate-200 mx-1" />
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          className={`h-8 px-2 ${editor.isActive('heading', { level: 1 }) ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-h1"
        >
          H1
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          className={`h-8 px-2 ${editor.isActive('heading', { level: 2 }) ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-h2"
        >
          H2
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          className={`h-8 px-2 ${editor.isActive('heading', { level: 3 }) ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-h3"
        >
          H3
        </Button>
        <div className="w-px h-8 bg-slate-200 mx-1" />
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          className={`h-8 w-8 p-0 ${editor.isActive('bulletList') ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-bullet-list"
        >
          <List className="h-4 w-4" />
        </Button>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          className={`h-8 w-8 p-0 ${editor.isActive('orderedList') ? 'bg-slate-200' : ''}`}
          data-testid="toolbar-ordered-list"
        >
          <ListOrdered className="h-4 w-4" />
        </Button>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
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
          <div className="flex items-center space-x-3">
            <Button
              onClick={handleSave}
              disabled={saving}
              className="bg-primary hover:bg-primary/90 text-white h-10 px-4 rounded-sm font-sans"
              data-testid="save-conclusion-btn"
            >
              {saving ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <Save className="h-4 w-4 mr-2" />
              )}
              Sauvegarder
            </Button>
            <Button
              onClick={handleExportPDF}
              variant="outline"
              className="h-10 px-4 rounded-sm font-sans border-slate-300"
              data-testid="export-pdf-btn"
            >
              <FileDown className="h-4 w-4 mr-2" />
              Export PDF
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card className="border-slate-200 rounded-sm">
              <CardHeader>
                <CardTitle className="font-serif text-2xl text-primary">
                  {conclusion.type === 'jaf' ? 'Conclusion JAF' : 'Conclusion Pénale'}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="border border-slate-200 rounded-sm overflow-hidden">
                  <EditorToolbar />
                  <EditorContent 
                    editor={editor} 
                    className="bg-white"
                    data-testid="tiptap-editor"
                  />
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card className="border-slate-200 rounded-sm">
              <CardHeader>
                <CardTitle className="font-serif text-xl text-primary">Rechercher dans le Code Civil</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-2">
                  <Input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSearchArticles()}
                    placeholder="Ex: autorité parentale"
                    className="h-10 rounded-sm border-slate-200 font-sans"
                    data-testid="search-code-civil-input"
                  />
                  <Button
                    onClick={handleSearchArticles}
                    disabled={searchingArticles}
                    className="bg-primary hover:bg-primary/90 text-white h-10 px-4 rounded-sm"
                    data-testid="search-code-civil-btn"
                  >
                    {searchingArticles ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Search className="h-4 w-4" />
                    )}
                  </Button>
                </div>

                {articles.length > 0 && (
                  <Accordion type="single" collapsible className="w-full">
                    {articles.map((article) => (
                      <AccordionItem key={article.article_id} value={article.article_id}>
                        <AccordionTrigger className="font-sans text-sm font-medium text-left">
                          Article {article.numero} - {article.titre}
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-3">
                            <p className="text-sm text-slate-600 font-sans leading-relaxed">
                              {article.contenu}
                            </p>
                            <Button
                              onClick={() => insertArticle(article)}
                              size="sm"
                              variant="outline"
                              className="w-full rounded-sm border-slate-300 font-sans"
                            >
                              Insérer cet article
                            </Button>
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    ))}
                  </Accordion>
                )}
              </CardContent>
            </Card>

            <Card className="border-slate-200 rounded-sm">
              <CardHeader>
                <CardTitle className="font-serif text-xl text-primary">Détails de l'affaire</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs font-sans font-medium text-slate-500 mb-1">TRIBUNAL</p>
                  <p className="text-sm font-sans text-slate-700">{conclusion.parties.tribunal || 'Non renseigné'}</p>
                </div>
                <div>
                  <p className="text-xs font-sans font-medium text-slate-500 mb-1">NUMÉRO RG</p>
                  <p className="text-sm font-sans text-slate-700">{conclusion.parties.numeroRG || 'Non renseigné'}</p>
                </div>
                <div>
                  <p className="text-xs font-sans font-medium text-slate-500 mb-1">DEMANDEUR</p>
                  <p className="text-sm font-sans text-slate-700">{conclusion.parties.demandeur || 'Non renseigné'}</p>
                </div>
                <div>
                  <p className="text-xs font-sans font-medium text-slate-500 mb-1">DÉFENDEUR</p>
                  <p className="text-sm font-sans text-slate-700">{conclusion.parties.defendeur || 'Non renseigné'}</p>
                </div>
              </CardContent>
            </Card>

            {/* Pieces Manager */}
            <PiecesManager
              conclusionId={conclusionId}
              pieces={pieces}
              setPieces={setPieces}
              onInsertReference={handleInsertPieceReference}
            />

            {/* Insert Bordereau Button */}
            {pieces.length > 0 && (
              <Button
                onClick={handleInsertBordereau}
                variant="outline"
                className="w-full border-slate-300 text-slate-700 hover:text-primary hover:border-primary/50"
                data-testid="insert-bordereau-btn"
              >
                <FileText className="h-4 w-4 mr-2" />
                Insérer le bordereau de pièces
              </Button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default ConclusionEditor;