import React, { useEffect, useState, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Scale, CheckCircle, Loader2, XCircle } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const PaymentSuccess = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [status, setStatus] = useState('checking');
  const [paymentInfo, setPaymentInfo] = useState(null);
  const hasPolled = useRef(false);

  useEffect(() => {
    if (hasPolled.current) return;
    hasPolled.current = true;

    const sessionId = new URLSearchParams(location.search).get('session_id');

    if (!sessionId) {
      setStatus('error');
      return;
    }

    pollPaymentStatus(sessionId);
  }, [location]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;

    if (attempts >= maxAttempts) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/payments/status/${sessionId}`,
        { withCredentials: true }
      );

      setPaymentInfo(response.data);

      if (response.data.payment_status === 'paid') {
        setStatus('success');
        return;
      } else if (response.data.status === 'expired') {
        setStatus('expired');
        return;
      }

      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), 2000);
    } catch (error) {
      console.error('Error checking payment:', error);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <nav className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center space-x-2">
            <Scale className="h-8 w-8 text-primary" strokeWidth={1.5} />
            <span className="font-serif text-2xl font-semibold text-primary">ConclusioPro</span>
          </div>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-6 py-16">
        <Card className="border-slate-200 rounded-sm">
          <CardHeader className="text-center pb-8">
            {status === 'checking' && (
              <>
                <Loader2 className="h-16 w-16 text-primary mx-auto mb-4 animate-spin" />
                <CardTitle className="font-serif text-3xl text-primary">
                  Vérification du paiement...
                </CardTitle>
              </>
            )}

            {status === 'success' && (
              <>
                <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" strokeWidth={1.5} />
                <CardTitle className="font-serif text-3xl text-primary mb-2">
                  Paiement confirmé !
                </CardTitle>
                <p className="text-slate-600 font-sans">
                  Votre crédit a été ajouté à votre compte
                </p>
              </>
            )}

            {(status === 'error' || status === 'expired' || status === 'timeout') && (
              <>
                <XCircle className="h-16 w-16 text-red-600 mx-auto mb-4" strokeWidth={1.5} />
                <CardTitle className="font-serif text-3xl text-primary mb-2">
                  {status === 'expired' ? 'Session expirée' : 'Erreur de paiement'}
                </CardTitle>
                <p className="text-slate-600 font-sans">
                  {status === 'timeout' 
                    ? 'La vérification a pris trop de temps. Vérifiez votre email.'
                    : 'Une erreur est survenue lors de la vérification du paiement.'}
                </p>
              </>
            )}
          </CardHeader>

          <CardContent className="space-y-6">
            {paymentInfo && status === 'success' && (
              <div className="bg-green-50 border border-green-200 rounded-sm p-6 space-y-2">
                <p className="font-sans text-sm text-slate-700">
                  <strong>Montant :</strong> {paymentInfo.amount}€
                </p>
                <p className="font-sans text-sm text-slate-700">
                  <strong>Crédit ajouté :</strong> 1 document
                </p>
                <p className="font-sans text-sm text-slate-700">
                  <strong>Statut :</strong> Payé ✓
                </p>
              </div>
            )}

            <div className="flex flex-col gap-3">
              {status === 'success' && (
                <Button
                  onClick={() => navigate('/new-conclusion')}
                  className="w-full h-12 bg-accent hover:bg-accent/90 text-white rounded-sm font-sans font-medium"
                >
                  Créer ma conclusion
                </Button>
              )}
              <Button
                onClick={() => navigate('/dashboard')}
                variant="outline"
                className="w-full h-12 rounded-sm border-slate-300 font-sans"
              >
                Retour au Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default PaymentSuccess;