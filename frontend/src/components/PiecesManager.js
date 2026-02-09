import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { 
  Upload, 
  FileText, 
  Trash2, 
  Edit2, 
  Check, 
  X, 
  GripVertical,
  Download,
  Plus,
  FileImage,
  FileSpreadsheet,
  File,
  Eye,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB

// Check if file type is previewable
const isPreviewable = (mimeType) => {
  return mimeType.startsWith('image/') || mimeType === 'application/pdf';
};

const getFileIcon = (mimeType) => {
  if (mimeType.startsWith('image/')) {
    return <FileImage className="h-5 w-5 text-blue-500" />;
  } else if (mimeType.includes('pdf')) {
    return <FileText className="h-5 w-5 text-red-500" />;
  } else if (mimeType.includes('spreadsheet') || mimeType.includes('excel')) {
    return <FileSpreadsheet className="h-5 w-5 text-green-500" />;
  } else if (mimeType.includes('word') || mimeType.includes('document')) {
    return <FileText className="h-5 w-5 text-blue-600" />;
  }
  return <File className="h-5 w-5 text-gray-500" />;
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' o';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' Ko';
  return (bytes / (1024 * 1024)).toFixed(1) + ' Mo';
};

const PiecesManager = ({ conclusionId, pieces, setPieces, onInsertReference }) => {
  const [uploading, setUploading] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [editingPiece, setEditingPiece] = useState(null);
  const [draggedPiece, setDraggedPiece] = useState(null);
  const [previewPiece, setPreviewPiece] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const fileInputRef = useRef(null);
  // Upload form state
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadNom, setUploadNom] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    if (file.size > MAX_FILE_SIZE) {
      toast.error('Le fichier dépasse la taille maximale de 10 Mo');
      return;
    }
    
    setUploadFile(file);
    // Pre-fill name with filename without extension
    const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
    setUploadNom(nameWithoutExt);
    setShowUploadDialog(true);
  };

  const handleUpload = async () => {
    if (!uploadFile || !uploadNom.trim()) {
      toast.error('Veuillez remplir le nom de la pièce');
      return;
    }

    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadFile);
      formData.append('nom', uploadNom.trim());
      formData.append('description', uploadDescription.trim());

      const response = await axios.post(
        `${BACKEND_URL}/api/conclusions/${conclusionId}/pieces`,
        formData,
        {
          withCredentials: true,
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      );

      setPieces([...pieces, response.data]);
      toast.success(`Pièce n°${response.data.numero} ajoutée`);
      
      // Reset form
      setShowUploadDialog(false);
      setUploadFile(null);
      setUploadNom('');
      setUploadDescription('');
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error('Error uploading piece:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  const handleUpdatePiece = async (pieceId, updates) => {
    try {
      const response = await axios.put(
        `${BACKEND_URL}/api/conclusions/${conclusionId}/pieces/${pieceId}`,
        updates,
        { withCredentials: true }
      );

      setPieces(pieces.map(p => p.piece_id === pieceId ? response.data : p));
      setEditingPiece(null);
      toast.success('Pièce mise à jour');
    } catch (error) {
      console.error('Error updating piece:', error);
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDeletePiece = async (pieceId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cette pièce ?')) {
      return;
    }

    try {
      await axios.delete(
        `${BACKEND_URL}/api/conclusions/${conclusionId}/pieces/${pieceId}`,
        { withCredentials: true }
      );

      // Update local state - pieces will be renumbered by backend
      const updatedPieces = pieces
        .filter(p => p.piece_id !== pieceId)
        .map((p, idx) => ({ ...p, numero: idx + 1 }));
      setPieces(updatedPieces);
      toast.success('Pièce supprimée');
    } catch (error) {
      console.error('Error deleting piece:', error);
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleDownload = async (piece) => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/pieces/${piece.piece_id}/download`,
        {
          withCredentials: true,
          responseType: 'blob'
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', piece.original_filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading piece:', error);
      toast.error('Erreur lors du téléchargement');
    }
  };

  const handlePreview = async (piece) => {
    if (!isPreviewable(piece.mime_type)) {
      toast.info('Aperçu non disponible pour ce type de fichier');
      return;
    }

    setLoadingPreview(true);
    setPreviewPiece(piece);

    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/pieces/${piece.piece_id}/download`,
        {
          withCredentials: true,
          responseType: 'blob'
        }
      );

      const blob = new Blob([response.data], { type: piece.mime_type });
      const url = window.URL.createObjectURL(blob);
      setPreviewUrl(url);
    } catch (error) {
      console.error('Error loading preview:', error);
      toast.error('Erreur lors du chargement de l\'aperçu');
      setPreviewPiece(null);
    } finally {
      setLoadingPreview(false);
    }
  };

  const closePreview = () => {
    if (previewUrl) {
      window.URL.revokeObjectURL(previewUrl);
    }
    setPreviewPiece(null);
    setPreviewUrl(null);
  };

  // Drag and drop handlers
  const handleDragStart = (e, piece) => {
    setDraggedPiece(piece);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e, targetPiece) => {
    e.preventDefault();
    if (!draggedPiece || draggedPiece.piece_id === targetPiece.piece_id) {
      setDraggedPiece(null);
      return;
    }

    // Reorder pieces
    const newPieces = [...pieces];
    const draggedIndex = newPieces.findIndex(p => p.piece_id === draggedPiece.piece_id);
    const targetIndex = newPieces.findIndex(p => p.piece_id === targetPiece.piece_id);

    newPieces.splice(draggedIndex, 1);
    newPieces.splice(targetIndex, 0, draggedPiece);

    // Update local state immediately
    const reorderedPieces = newPieces.map((p, idx) => ({ ...p, numero: idx + 1 }));
    setPieces(reorderedPieces);

    // Update server
    try {
      await axios.put(
        `${BACKEND_URL}/api/conclusions/${conclusionId}/pieces/reorder`,
        { piece_ids: newPieces.map(p => p.piece_id) },
        { withCredentials: true }
      );
      toast.success('Ordre mis à jour');
    } catch (error) {
      console.error('Error reordering pieces:', error);
      toast.error('Erreur lors de la réorganisation');
    }

    setDraggedPiece(null);
  };

  return (
    <Card className="border-slate-200 rounded-sm">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="font-serif text-xl text-primary">Pièces jointes</CardTitle>
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            accept="*/*"
            data-testid="piece-file-input"
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            size="sm"
            className="bg-primary hover:bg-primary/90 text-white rounded-sm"
            data-testid="add-piece-btn"
          >
            <Plus className="h-4 w-4 mr-1" />
            Ajouter
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {pieces.length === 0 ? (
          <div 
            className="border-2 border-dashed border-slate-200 rounded-sm p-6 text-center cursor-pointer hover:border-primary/50 transition-colors"
            onClick={() => fileInputRef.current?.click()}
            data-testid="drop-zone"
          >
            <Upload className="h-8 w-8 mx-auto text-slate-400 mb-2" />
            <p className="text-sm text-slate-500">
              Cliquez ou glissez-déposez vos fichiers ici
            </p>
            <p className="text-xs text-slate-400 mt-1">
              PDF, Images, Word... (max 10 Mo)
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {pieces.map((piece) => (
              <div
                key={piece.piece_id}
                draggable
                onDragStart={(e) => handleDragStart(e, piece)}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, piece)}
                className={`flex items-center gap-3 p-3 bg-slate-50 rounded-sm border border-slate-200 group hover:border-primary/30 transition-colors ${
                  draggedPiece?.piece_id === piece.piece_id ? 'opacity-50' : ''
                }`}
                data-testid={`piece-item-${piece.numero}`}
              >
                <div className="cursor-grab text-slate-400 hover:text-slate-600">
                  <GripVertical className="h-4 w-4" />
                </div>
                
                <div className="flex-shrink-0">
                  {getFileIcon(piece.mime_type)}
                </div>

                <div className="flex-grow min-w-0">
                  {editingPiece?.piece_id === piece.piece_id ? (
                    <div className="space-y-2">
                      <Input
                        value={editingPiece.nom}
                        onChange={(e) => setEditingPiece({ ...editingPiece, nom: e.target.value })}
                        className="h-8 text-sm"
                        placeholder="Nom de la pièce"
                        data-testid="edit-piece-nom"
                      />
                      <Input
                        value={editingPiece.description || ''}
                        onChange={(e) => setEditingPiece({ ...editingPiece, description: e.target.value })}
                        className="h-8 text-sm"
                        placeholder="Description (optionnel)"
                        data-testid="edit-piece-description"
                      />
                    </div>
                  ) : (
                    <>
                      <p className="text-sm font-medium text-slate-700 truncate">
                        <span className="text-primary font-semibold">Pièce n°{piece.numero}</span>
                        {' - '}{piece.nom}
                      </p>
                      {piece.description && (
                        <p className="text-xs text-slate-500 truncate">{piece.description}</p>
                      )}
                      <p className="text-xs text-slate-400">{formatFileSize(piece.file_size)}</p>
                    </>
                  )}
                </div>

                <div className="flex items-center gap-1 flex-shrink-0">
                  {editingPiece?.piece_id === piece.piece_id ? (
                    <>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleUpdatePiece(piece.piece_id, {
                          nom: editingPiece.nom,
                          description: editingPiece.description
                        })}
                        className="h-8 w-8 p-0 text-green-600 hover:text-green-700"
                        data-testid="save-edit-btn"
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setEditingPiece(null)}
                        className="h-8 w-8 p-0 text-slate-500 hover:text-slate-700"
                        data-testid="cancel-edit-btn"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </>
                  ) : (
                    <>
                      {isPreviewable(piece.mime_type) && (
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handlePreview(piece)}
                          className="h-8 w-8 p-0 text-slate-500 hover:text-primary"
                          title="Aperçu"
                          data-testid={`preview-piece-btn-${piece.numero}`}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => onInsertReference(piece)}
                        className="h-8 px-2 text-xs text-primary hover:text-primary/80 opacity-0 group-hover:opacity-100 transition-opacity"
                        title="Insérer référence"
                        data-testid={`insert-ref-btn-${piece.numero}`}
                      >
                        + Réf
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDownload(piece)}
                        className="h-8 w-8 p-0 text-slate-500 hover:text-slate-700"
                        title="Télécharger"
                        data-testid={`download-piece-btn-${piece.numero}`}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setEditingPiece({ ...piece })}
                        className="h-8 w-8 p-0 text-slate-500 hover:text-slate-700"
                        title="Modifier"
                        data-testid={`edit-piece-btn-${piece.numero}`}
                      >
                        <Edit2 className="h-4 w-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleDeletePiece(piece.piece_id)}
                        className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                        title="Supprimer"
                        data-testid={`delete-piece-btn-${piece.numero}`}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </>
                  )}
                </div>
              </div>
            ))}
            
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              className="w-full border-dashed border-slate-300 text-slate-500 hover:text-primary hover:border-primary/50"
              data-testid="add-more-pieces-btn"
            >
              <Plus className="h-4 w-4 mr-2" />
              Ajouter une pièce
            </Button>
          </div>
        )}

        {/* Bordereau de pièces summary */}
        {pieces.length > 0 && (
          <div className="mt-4 pt-4 border-t border-slate-200">
            <p className="text-xs font-medium text-slate-500 mb-2">BORDEREAU DE PIÈCES</p>
            <div className="bg-slate-100 p-3 rounded-sm text-xs space-y-1">
              {pieces.map((piece) => (
                <p key={piece.piece_id} className="text-slate-600">
                  <span className="font-medium">Pièce n°{piece.numero}</span> : {piece.nom}
                </p>
              ))}
            </div>
          </div>
        )}
      </CardContent>

      {/* Upload Dialog */}
      <Dialog open={showUploadDialog} onOpenChange={setShowUploadDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-serif text-primary">Ajouter une pièce</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            {uploadFile && (
              <div className="flex items-center gap-3 p-3 bg-slate-50 rounded-sm">
                {getFileIcon(uploadFile.type)}
                <div className="flex-grow min-w-0">
                  <p className="text-sm font-medium text-slate-700 truncate">{uploadFile.name}</p>
                  <p className="text-xs text-slate-400">{formatFileSize(uploadFile.size)}</p>
                </div>
              </div>
            )}
            <div className="space-y-2">
              <Label htmlFor="piece-nom">Nom de la pièce *</Label>
              <Input
                id="piece-nom"
                value={uploadNom}
                onChange={(e) => setUploadNom(e.target.value)}
                placeholder="Ex: Contrat de travail du 15/03/2023"
                data-testid="upload-piece-nom"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="piece-description">Description (optionnel)</Label>
              <Textarea
                id="piece-description"
                value={uploadDescription}
                onChange={(e) => setUploadDescription(e.target.value)}
                placeholder="Description ou commentaire sur cette pièce..."
                rows={2}
                data-testid="upload-piece-description"
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowUploadDialog(false);
                setUploadFile(null);
                setUploadNom('');
                setUploadDescription('');
              }}
              data-testid="cancel-upload-btn"
            >
              Annuler
            </Button>
            <Button
              onClick={handleUpload}
              disabled={uploading || !uploadNom.trim()}
              className="bg-primary hover:bg-primary/90 text-white"
              data-testid="confirm-upload-btn"
            >
              {uploading ? 'Upload...' : 'Ajouter la pièce'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={!!previewPiece} onOpenChange={(open) => !open && closePreview()}>
        <DialogContent className="sm:max-w-4xl max-h-[90vh] overflow-hidden">
          <DialogHeader>
            <DialogTitle className="font-serif text-primary flex items-center gap-2">
              {previewPiece && getFileIcon(previewPiece.mime_type)}
              <span>Pièce n°{previewPiece?.numero} - {previewPiece?.nom}</span>
            </DialogTitle>
          </DialogHeader>
          <div className="flex-1 min-h-[60vh] bg-slate-100 rounded-sm overflow-hidden">
            {loadingPreview ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <span className="ml-2 text-slate-500">Chargement de l'aperçu...</span>
              </div>
            ) : previewUrl && previewPiece ? (
              previewPiece.mime_type.startsWith('image/') ? (
                <div className="flex items-center justify-center h-full p-4">
                  <img
                    src={previewUrl}
                    alt={previewPiece.nom}
                    className="max-w-full max-h-[60vh] object-contain rounded shadow-lg"
                    data-testid="preview-image"
                  />
                </div>
              ) : previewPiece.mime_type === 'application/pdf' ? (
                <iframe
                  src={previewUrl}
                  title={previewPiece.nom}
                  className="w-full h-[60vh] border-0"
                  data-testid="preview-pdf"
                />
              ) : null
            ) : null}
          </div>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => handleDownload(previewPiece)}
              className="border-slate-300"
              data-testid="preview-download-btn"
            >
              <Download className="h-4 w-4 mr-2" />
              Télécharger
            </Button>
            <Button
              onClick={closePreview}
              className="bg-primary hover:bg-primary/90 text-white"
              data-testid="preview-close-btn"
            >
              Fermer
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </Card>
  );
};

export default PiecesManager;
