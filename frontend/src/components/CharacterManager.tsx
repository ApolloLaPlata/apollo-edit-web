import React, { useRef, useState, useEffect } from 'react';
import { Character, ApiKey } from '../types';
import toast from 'react-hot-toast';
import { Upload, Trash2, Tag, User, Plus, X, Pencil, Check, Wand2, Star } from 'lucide-react';
import { generateCharacterDescription } from '../services/geminiService';
import { executeWithKeyRotation } from '../utils/apiKeyRotation';

interface CharacterManagerProps {
  characters: Character[];
  onAddCharacter: (char: Character) => void;
  onUpdateCharacter: (char: Character) => void;
  onDeleteCharacter: (id: string) => void;
  apiKeys: ApiKey[];
  setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
}

interface CharacterCardProps {
    char: Character;
    onUpdate: (char: Character) => void;
    onDelete: (char: Character) => void;
    onRemoveImage: (id: string, idx: number) => void;
    onTriggerAddImage: (id: string) => void;
    onSetMainImage: (id: string, idx: number) => void;
    apiKeys: ApiKey[];
    setApiKeys: React.Dispatch<React.SetStateAction<ApiKey[]>>;
}

// Helper to read file as Base64 Promise and resize it
const readFileAsBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                const maxDim = 1024;

                if (width > height && width > maxDim) {
                    height *= maxDim / width;
                    width = maxDim;
                } else if (height > maxDim) {
                    width *= maxDim / height;
                    height = maxDim;
                }

                canvas.width = width;
                canvas.height = height;
                const ctx = canvas.getContext('2d');
                if (ctx) {
                    ctx.drawImage(img, 0, 0, width, height);
                    resolve(canvas.toDataURL(file.type || 'image/jpeg', 0.8));
                } else {
                    resolve(e.target?.result as string);
                }
            };
            img.onerror = reject;
            img.src = e.target?.result as string;
        };
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
};

const CharacterCard: React.FC<CharacterCardProps> = ({ 
    char, 
    onUpdate, 
    onDelete, 
    onRemoveImage, 
    onTriggerAddImage,
    onSetMainImage,
    apiKeys,
    setApiKeys
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [isGeneratingDesc, setIsGeneratingDesc] = useState(false);
    const [localName, setLocalName] = useState(char.name);
    const [localDescription, setLocalDescription] = useState(char.description || '');
    const [localCategory, setLocalCategory] = useState(char.category || '');
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    // Sync local state if external prop changes
    useEffect(() => {
        setLocalName(char.name);
        setLocalDescription(char.description || '');
        setLocalCategory(char.category || '');
    }, [char.name, char.description, char.category]);

    // Auto-focus input when entering edit mode
    useEffect(() => {
        if (isEditing && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isEditing]);

    const handleSave = () => {
        if (localName.trim() !== char.name || localDescription.trim() !== (char.description || '') || localCategory.trim() !== (char.category || '')) {
            onUpdate({
                ...char,
                name: localName.trim() || char.name,
                description: localDescription.trim(),
                category: localCategory.trim()
            });
        }
        setIsEditing(false);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSave();
        } else if (e.key === 'Escape') {
            setLocalName(char.name); // Revert
            setLocalDescription(char.description || '');
            setLocalCategory(char.category || '');
            setIsEditing(false);
        }
    };

    const handleGenerateDescription = async () => {
        if (char.images.length === 0) {
            toast.error("Adicione imagens de referência primeiro.");
            return;
        }
        
        setIsGeneratingDesc(true);
        try {
            // We use a ref to pass apiKeys to executeWithKeyRotation
            const apiKeysRef = { current: apiKeys };
            const description = await executeWithKeyRotation(
                apiKeysRef,
                setApiKeys,
                async (apiKey) => await generateCharacterDescription(apiKey, char.images)
            );
            setLocalDescription(description);
            toast.success("Descrição gerada com sucesso!");
        } catch (error: any) {
            toast.error("Falha ao gerar descrição: " + error.message);
        } finally {
            setIsGeneratingDesc(false);
        }
    };

    return (
        <div className="bg-slate-800 rounded-lg overflow-hidden border border-slate-700 shadow-md flex flex-col group hover:border-slate-600 transition-colors">
            {/* Header with Name */}
            <div className="p-3 bg-slate-900/50 border-b border-slate-700 flex flex-col gap-2">
                <div className="flex justify-between items-center gap-2 h-10">
                    {isEditing ? (
                        <div className="flex flex-col gap-2 flex-1 min-w-0 animate-in fade-in duration-200">
                            <input 
                                ref={inputRef}
                                className="bg-slate-950 text-white font-bold text-sm flex-1 min-w-0 outline-none border border-purple-500 rounded px-2 py-1"
                                value={localName}
                                onChange={(e) => setLocalName(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Nome / Tag (ex: #Hero)"
                            />
                            <div className="flex items-center gap-2">
                                <input 
                                    className="bg-slate-950 text-slate-300 text-xs flex-1 min-w-0 outline-none border border-slate-600 focus:border-purple-500 rounded px-2 py-1"
                                    value={localCategory}
                                    onChange={(e) => setLocalCategory(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Categoria (ex: Heróis)"
                                />
                                <button 
                                    onMouseDown={(e) => e.preventDefault()} // Prevent blur before click
                                    onClick={handleSave}
                                    className="bg-green-600/20 text-green-400 p-1.5 rounded hover:bg-green-600/40"
                                >
                                    <Check className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="flex flex-col gap-1 flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                                <span 
                                    className="font-bold text-sm text-white truncate flex-1 cursor-pointer hover:text-purple-300"
                                    onClick={() => setIsEditing(true)}
                                    title={char.name}
                                >
                                    {char.name}
                                </span>
                                {!showDeleteConfirm && (
                                    <button
                                        onClick={() => setIsEditing(true)}
                                        className="text-slate-500 hover:text-purple-400 p-1.5 rounded hover:bg-slate-800 opacity-0 group-hover:opacity-100 transition-opacity"
                                        title="Editar Personagem"
                                    >
                                        <Pencil className="w-3 h-3" />
                                    </button>
                                )}
                            </div>
                            {char.category && (
                                <span className="text-xs text-slate-400 bg-slate-800 px-2 py-0.5 rounded-full w-fit border border-slate-700">
                                    {char.category}
                                </span>
                            )}
                        </div>
                    )}
                    
                    {!isEditing && (
                        <div className="flex items-center">
                            {showDeleteConfirm ? (
                                <div className="flex items-center gap-2 animate-in slide-in-from-right fade-in duration-200">
                                    <span className="text-[10px] text-red-400 font-bold hidden sm:inline">Excluir?</span>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            onDelete(char);
                                        }}
                                        className="bg-red-600 text-white p-2 rounded hover:bg-red-700 transition-colors shadow-lg"
                                        title="Confirmar Exclusão"
                                    >
                                        <Check className="w-4 h-4" />
                                    </button>
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            setShowDeleteConfirm(false);
                                        }}
                                        className="bg-slate-700 text-slate-300 p-2 rounded hover:bg-slate-600 transition-colors"
                                        title="Cancelar"
                                    >
                                        <X className="w-4 h-4" />
                                    </button>
                                </div>
                            ) : (
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setShowDeleteConfirm(true);
                                    }}
                                    className="bg-slate-800 text-slate-400 hover:bg-red-900/50 hover:text-red-400 p-2 rounded transition-colors shadow-sm border border-slate-700 hover:border-red-500"
                                    title="Excluir Personagem"
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            )}
                        </div>
                    )}
                </div>
                
                {/* Description Field */}
                {isEditing ? (
                    <div className="flex flex-col gap-2">
                        <textarea
                            className="bg-slate-950 text-slate-300 text-xs outline-none border border-purple-500 rounded px-2 py-1 w-full resize-none h-24"
                            value={localDescription}
                            onChange={(e) => setLocalDescription(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Descreva as características físicas e roupas para forçar a consistência (ex: cabelo loiro curto, olhos azuis, jaqueta de couro preta)..."
                        />
                        <button
                            onClick={handleGenerateDescription}
                            disabled={isGeneratingDesc || char.images.length === 0}
                            className="flex items-center justify-center gap-2 bg-purple-600/20 hover:bg-purple-600/40 text-purple-400 text-xs py-1.5 px-3 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed border border-purple-500/30"
                            title="Gerar descrição baseada nas imagens de referência"
                        >
                            <Wand2 className={`w-3 h-3 ${isGeneratingDesc ? 'animate-spin' : ''}`} />
                            {isGeneratingDesc ? 'Analisando Imagens...' : 'Gerar Descrição com IA'}
                        </button>
                    </div>
                ) : (
                    char.description && (
                        <p className="text-xs text-slate-400 line-clamp-2 cursor-pointer hover:text-slate-300" onClick={() => setIsEditing(true)}>
                            {char.description}
                        </p>
                    )
                )}
            </div>

            {/* Image Grid */}
            <div className="p-3 bg-slate-800">
                <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-slate-600">
                    {char.images.map((img, idx) => {
                        const isMain = img === char.previewUrl;
                        return (
                            <div key={idx} className={`relative group/img flex-shrink-0 w-24 h-24 rounded overflow-hidden border bg-black ${isMain ? 'border-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]' : 'border-slate-600'}`}>
                                <img src={img} alt={`${char.name}-${idx}`} className="w-full h-full object-cover" />
                                
                                {isMain && (
                                    <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-[8px] text-amber-400 font-bold text-center py-0.5">
                                        PRINCIPAL
                                    </div>
                                )}
                                
                                <div className="absolute top-1 right-1 flex flex-col gap-1 opacity-0 group-hover/img:opacity-100 transition-all z-20">
                                    <button 
                                        type="button"
                                        onClick={() => onRemoveImage(char.id, idx)}
                                        className="bg-black/60 hover:bg-red-600 text-white p-1 rounded-full cursor-pointer"
                                        title="Remover imagem"
                                    >
                                        <X className="w-3 h-3 pointer-events-none" />
                                    </button>
                                    {!isMain && (
                                        <button 
                                            type="button"
                                            onClick={() => onSetMainImage(char.id, idx)}
                                            className="bg-black/60 hover:bg-amber-500 text-white p-1 rounded-full cursor-pointer"
                                            title="Definir como Principal"
                                        >
                                            <Star className="w-3 h-3 pointer-events-none" />
                                        </button>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                    {/* Add Image Button */}
                    <button 
                        type="button"
                        onClick={() => onTriggerAddImage(char.id)}
                        className="flex-shrink-0 w-24 h-24 rounded border border-dashed border-slate-600 flex flex-col items-center justify-center text-slate-500 hover:bg-slate-700/50 hover:text-purple-400 transition-colors"
                        title="Adicionar pose extra"
                    >
                        <Plus className="w-6 h-6 mb-1 pointer-events-none" />
                        <span className="text-[10px] pointer-events-none">Add Pose</span>
                    </button>
                </div>
                <div className="flex justify-between items-center mt-2">
                    <span className="text-[10px] text-slate-500 font-mono bg-slate-900/50 px-2 py-0.5 rounded">
                        ID: {char.id.slice(0,4)}
                    </span>
                    <span className="text-[10px] text-slate-400">
                        {char.images.length} pose(s)
                    </span>
                </div>
            </div>
        </div>
    );
};

const CharacterManager: React.FC<CharacterManagerProps> = ({ 
    characters, 
    onAddCharacter, 
    onUpdateCharacter, 
    onDeleteCharacter,
    apiKeys,
    setApiKeys
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const addImageInputRef = useRef<HTMLInputElement>(null);
  const [newCharName, setNewCharName] = useState('');
  const [newCharCategory, setNewCharCategory] = useState('');
  const [activeCharIdForAdd, setActiveCharIdForAdd] = useState<string | null>(null);

  // New Character Creation (Multiple Files)
  const handleNewCharacterFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const files = Array.from(e.target.files);
      
      try {
          const base64Images = await Promise.all(files.map(readFileAsBase64));
          
          // Default name if empty
          const nameToUse = newCharName.trim() || `#Personagem${characters.length + 1}`;
          const finalName = nameToUse.startsWith('#') ? nameToUse : `#${nameToUse}`;
          
          const newCharacter: Character = {
            id: crypto.randomUUID(),
            name: finalName,
            category: newCharCategory.trim() || undefined,
            images: base64Images, // Store all selected images
            previewUrl: base64Images[0], // Use first one as main preview
          };

          onAddCharacter(newCharacter);
          setNewCharName(''); // Reset input
          setNewCharCategory(''); // Reset category
          
          // Reset file input value
          if (fileInputRef.current) fileInputRef.current.value = '';

      } catch (error) {
          console.error("Error reading files", error);
          toast.error("Erro ao ler arquivos de imagem.");
      }
    }
  };

  // Add extra images to existing character (Multiple Files)
  const handleAddImageToCharacter = async (e: React.ChangeEvent<HTMLInputElement>) => {
      if (activeCharIdForAdd && e.target.files && e.target.files.length > 0) {
          const files = Array.from(e.target.files);
          
          try {
              const base64Images = await Promise.all(files.map(readFileAsBase64));
              
              const charToUpdate = characters.find(c => c.id === activeCharIdForAdd);
              if (charToUpdate) {
                  onUpdateCharacter({
                      ...charToUpdate,
                      images: [...charToUpdate.images, ...base64Images]
                  });
              }
              setActiveCharIdForAdd(null);
              if (addImageInputRef.current) addImageInputRef.current.value = '';

          } catch (error) {
              console.error("Error reading files", error);
              toast.error("Erro ao adicionar novas poses.");
          }
      }
  };

  const triggerAddImage = (charId: string) => {
      setActiveCharIdForAdd(charId);
      setTimeout(() => {
          addImageInputRef.current?.click();
      }, 0);
  };

  const handleRemoveCharacter = (char: Character) => {
    // Direct delete call without window.confirm, as UI handles confirmation now
    onDeleteCharacter(char.id);
  };

  const removeImageFromCharacter = (charId: string, imgIndex: number) => {
      const charToUpdate = characters.find(c => c.id === charId);
      if (charToUpdate) {
          const newImages = charToUpdate.images.filter((_, idx) => idx !== imgIndex);
          onUpdateCharacter({
              ...charToUpdate,
              images: newImages,
              previewUrl: newImages.length > 0 ? newImages[0] : (charToUpdate.previewUrl || '')
          });
      }
  };

  const setMainImage = (charId: string, imgIndex: number) => {
      const charToUpdate = characters.find(c => c.id === charId);
      if (charToUpdate) {
          const selectedImage = charToUpdate.images[imgIndex];
          // Bring it to the front so it acts as standard preview list leader
          const reorderedImages = [
              selectedImage,
              ...charToUpdate.images.filter((_, idx) => idx !== imgIndex)
          ];
          onUpdateCharacter({
              ...charToUpdate,
              previewUrl: selectedImage,
              images: reorderedImages
          });
          toast.success("Imagem definida como Principal.");
      }
  };

  // Group and sort characters
  const groupedCharacters = characters.reduce((acc, char) => {
      const category = char.category || 'Sem Categoria';
      if (!acc[category]) {
          acc[category] = [];
      }
      acc[category].push(char);
      return acc;
  }, {} as Record<string, Character[]>);

  // Sort categories alphabetically, but keep "Sem Categoria" at the end
  const sortedCategories = Object.keys(groupedCharacters).sort((a, b) => {
      if (a === 'Sem Categoria') return 1;
      if (b === 'Sem Categoria') return -1;
      return a.localeCompare(b);
  });

  // Sort characters within each category alphabetically
  sortedCategories.forEach(category => {
      groupedCharacters[category].sort((a, b) => a.name.localeCompare(b.name));
  });

  return (
    <div className="h-full flex flex-col bg-slate-900 rounded-xl border border-slate-700 overflow-hidden">
      <div className="p-6 border-b border-slate-700">
        <h2 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
          <User className="w-5 h-5 text-purple-400" />
          Gerenciador de Personagens
        </h2>
        <p className="text-sm text-slate-400 mb-4">
          Gerencie seus "Tags Visuais" aqui. Se você cadastrou algo errado, clique no ícone da lixeira no cartão do personagem para removê-lo.
        </p>

        <div className="flex flex-col sm:flex-row gap-3 bg-slate-800 p-3 rounded-lg border border-slate-700">
          <div className="relative flex-1">
             <Tag className="absolute left-3 top-2.5 w-4 h-4 text-orange-400" />
            <input
              type="text"
              value={newCharName}
              onChange={(e) => setNewCharName(e.target.value)}
              placeholder="Nome da Tag (ex: #Heroi)"
              className="w-full bg-slate-900 border border-slate-600 rounded pl-9 pr-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
            />
          </div>
          <div className="relative flex-1">
            <input
              type="text"
              value={newCharCategory}
              onChange={(e) => setNewCharCategory(e.target.value)}
              placeholder="Categoria (ex: Heróis)"
              className="w-full bg-slate-900 border border-slate-600 rounded px-3 py-2 text-white focus:ring-2 focus:ring-purple-500 outline-none"
            />
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={!newCharName.trim()}
            className="bg-purple-600 hover:bg-purple-700 disabled:bg-slate-700 disabled:text-slate-500 text-white px-4 py-2 rounded flex items-center justify-center gap-2 transition-colors whitespace-nowrap font-bold shadow-lg"
          >
            <Upload className="w-4 h-4" /> Criar Personagem (Multi-Img)
          </button>
          {/* Added 'multiple' attribute */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleNewCharacterFile}
            accept="image/*"
            multiple 
            className="hidden"
          />
          {/* Added 'multiple' attribute */}
          <input
            type="file"
            ref={addImageInputRef}
            onChange={handleAddImageToCharacter}
            accept="image/*"
            multiple
            className="hidden"
          />
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6 bg-slate-950/30">
        {characters.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 space-y-4">
                <div className="w-20 h-20 rounded-full bg-slate-900 border border-slate-700 flex items-center justify-center">
                    <User className="w-10 h-10 opacity-20" />
                </div>
                <div className="text-center">
                    <p className="font-bold">Nenhum personagem registrado</p>
                    <p className="text-sm">Use o formulário acima para adicionar sua primeira referência.</p>
                </div>
            </div>
        ) : (
            <div className="space-y-8">
                {sortedCategories.map(category => (
                    <div key={category} className="space-y-4">
                        <h3 className="text-lg font-bold text-slate-300 border-b border-slate-800 pb-2">
                            {category} <span className="text-sm font-normal text-slate-500 ml-2">({groupedCharacters[category].length})</span>
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                            {groupedCharacters[category].map((char) => (
                                <CharacterCard 
                                    key={char.id}
                                    char={char}
                                    onUpdate={onUpdateCharacter}
                                    onDelete={handleRemoveCharacter}
                                    onRemoveImage={removeImageFromCharacter}
                                    onTriggerAddImage={triggerAddImage}
                                    onSetMainImage={setMainImage}
                                    apiKeys={apiKeys}
                                    setApiKeys={setApiKeys}
                                />
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        )}
      </div>
    </div>
  );
};

export default CharacterManager;