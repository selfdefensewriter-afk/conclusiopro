import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Scale, Plus, FileText, Calendar, LogOut } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const Dashboard = ({ user }) => {
  const navigate = useNavigate();
  const [conclusions, setConclusions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchConclusions();
  }, []);

  const fetchConclusions = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/conclusions`, {
        withCredentials: true
      });
      setConclusions(response.data);
    } catch (error) {
      console.error('Error fetching conclusions:', error);
      toast.error('Erreur lors du chargement des conclusions');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${BACKEND_URL}/api/auth/logout`, {}, {
        withCredentials: true
      });
      toast.success('Déconnexion réussie');
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
      toast.error('Erreur lors de la déconnexion');
    }
  };

  const handleDeleteConclusion = async (conclusionId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette conclusion ?')) {
      return;
    }

    try {
      await axios.delete(`${BACKEND_URL}/api/conclusions/${conclusionId}`, {
        withCredentials: true
      });
      toast.success('Conclusion supprimée');
      fetchConclusions();
    } catch (error) {
      console.error('Error deleting conclusion:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Scale className="h-8 w-8 text-primary" strokeWidth={1.5} />
            <span className="font-serif text-2xl font-semibold text-primary">ConclusioPro</span>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 px-4 py-2 bg-accent/10 rounded-sm border border-accent/20" data-testid="user-credits">
              <span className="font-sans text-sm text-slate-600">Crédits:</span>
              <span className="font-sans font-bold text-accent">{user?.credits || 0}</span>
            </div>
            <span className="font-sans text-slate-600" data-testid="user-name">Bonjour, {user?.name}</span>
            <Button 
              onClick={handleLogout}
              variant="outline"
              className="h-10 px-4 rounded-sm font-sans border-slate-300"
              data-testid="logout-btn"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Déconnexion
            </Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-serif text-4xl font-semibold text-primary mb-2">Mes conclusions</h1>
            <p className="font-sans text-slate-600">Gérez vos documents juridiques</p>
          </div>
          <div className="flex items-center gap-3">
            {user?.credits > 0 ? (
              <Button 
                onClick={() => navigate('/new-conclusion')}
                className="bg-accent hover:bg-accent/90 text-white h-12 px-6 rounded-sm font-sans font-medium"
                data-testid="new-conclusion-btn"
              >
                <Plus className="h-5 w-5 mr-2" />
                Nouvelle conclusion
              </Button>
            ) : (
              <>
                <Button 
                  onClick={() => navigate('/tarifs')}
                  className="bg-accent hover:bg-accent/90 text-white h-12 px-6 rounded-sm font-sans font-medium"
                  data-testid="buy-credits-btn"
                >
                  Acheter des crédits (29€)
                </Button>
                <Button 
                  onClick={() => navigate('/new-conclusion')}
                  variant="outline"
                  className="h-12 px-6 rounded-sm border-slate-300 font-sans"
                  data-testid="new-conclusion-btn"
                >
                  <Plus className="h-5 w-5 mr-2" />
                  Nouvelle conclusion
                </Button>
              </>
            )}
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : conclusions.length === 0 ? (
          <Card className="border-slate-200 rounded-sm" data-testid="empty-state">
            <CardContent className="py-16 text-center">
              <FileText className="h-16 w-16 text-slate-300 mx-auto mb-4" strokeWidth={1.5} />
              <h3 className="font-serif text-xl font-semibold text-slate-700 mb-2">
                Aucune conclusion pour le moment
              </h3>
              <p className="font-sans text-slate-500 mb-6">
                Commencez par créer votre première conclusion juridique
              </p>
              <Button 
                onClick={() => navigate('/new-conclusion')}
                className="bg-primary hover:bg-primary/90 text-white h-12 px-6 rounded-sm font-sans font-medium"
              >
                <Plus className="h-5 w-5 mr-2" />
                Créer ma première conclusion
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {conclusions.map((conclusion) => (
              <Card 
                key={conclusion.conclusion_id} 
                className="border-slate-200 rounded-sm card-hover cursor-pointer"
                onClick={() => navigate(`/conclusion/${conclusion.conclusion_id}`)}
                data-testid={`conclusion-card-${conclusion.conclusion_id}`}
              >
                <CardHeader>
                  <CardTitle className="font-serif text-xl text-primary">
                    {conclusion.type === 'jaf' ? 'Affaire JAF' : 'Affaire Pénale'}
                  </CardTitle>
                  <CardDescription className="font-sans">
                    <div className="flex items-center text-sm text-slate-500 mt-2">
                      <Calendar className="h-4 w-4 mr-2" />
                      {formatDate(conclusion.created_at)}
                    </div>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="inline-block px-3 py-1 bg-slate-100 text-slate-700 text-xs font-sans rounded-sm">
                      {conclusion.status === 'draft' ? 'Brouillon' : 
                       conclusion.status === 'completed' ? 'Terminé' : 'En cours'}
                    </div>
                    {conclusion.conclusion_text && (
                      <p className="text-sm text-slate-600 font-sans line-clamp-3 mt-3">
                        {conclusion.conclusion_text.substring(0, 150)}...
                      </p>
                    )}
                  </div>
                  <div className="mt-4 pt-4 border-t border-slate-100 flex gap-2">
                    <Button 
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate(`/conclusion/${conclusion.conclusion_id}`);
                      }}
                      variant="outline"
                      size="sm"
                      className="flex-1 rounded-sm border-slate-300"
                    >
                      Modifier
                    </Button>
                    <Button 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDeleteConclusion(conclusion.conclusion_id);
                      }}
                      variant="outline"
                      size="sm"
                      className="rounded-sm border-slate-300 text-red-600 hover:text-red-700"
                    >
                      Supprimer
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default Dashboard;