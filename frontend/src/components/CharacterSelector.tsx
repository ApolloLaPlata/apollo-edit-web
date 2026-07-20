import React, { useState, useMemo } from 'react';
import { Character } from '../types';
import { Search, Users, UserPlus } from 'lucide-react';

interface CharacterSelectorProps {
    characters: Character[];
    onSelect: (char: Character) => void;
    selectedIds?: string[]; // Optional: for toggle mode
    mode: 'insert' | 'toggle'; // 'insert' for ImageStudio, 'toggle' for ScriptRoom
    label?: string;
    icon?: React.ReactNode;
}

const CharacterSelector: React.FC<CharacterSelectorProps> = ({ 
    characters, 
    onSelect, 
    selectedIds = [], 
    mode,
    label,
    icon
}) => {
    const [searchQuery, setSearchQuery] = useState('');

    const filteredCharacters = useMemo(() => {
        if (!searchQuery.trim()) return characters;
        const query = searchQuery.toLowerCase();
        return characters.filter(char => 
            char.name.toLowerCase().includes(query) || 
            (char.category && char.category.toLowerCase().includes(query))
        );
    }, [characters, searchQuery]);

    const groupedCharacters = useMemo(() => {
        return filteredCharacters.reduce((acc, char) => {
            const category = char.category || 'Sem Categoria';
            if (!acc[category]) {
                acc[category] = [];
            }
            acc[category].push(char);
            return acc;
        }, {} as Record<string, Character[]>);
    }, [filteredCharacters]);

    const sortedCategories = useMemo(() => {
        const categories = Object.keys(groupedCharacters).sort((a, b) => {
            if (a === 'Sem Categoria') return 1;
            if (b === 'Sem Categoria') return -1;
            return a.localeCompare(b);
        });
        
        categories.forEach(category => {
            groupedCharacters[category].sort((a, b) => a.name.localeCompare(b.name));
        });
        
        return categories;
    }, [groupedCharacters]);

    if (!characters || characters.length === 0) return null;

    return (
        <div className="space-y-3">
            <div className="flex items-center justify-between">
                <label className="text-xs font-bold text-slate-400 uppercase flex items-center gap-2">
                    {icon || (mode === 'insert' ? <Users className="w-4 h-4 text-emerald-400" /> : <UserPlus className="w-4 h-4 text-emerald-400" />)}
                    {label || (mode === 'insert' ? 'Personagens (Clique para inserir no prompt)' : 'Personagens Selecionados')}
                </label>
            </div>
            
            {characters.length > 5 && (
                <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Search className="h-4 w-4 text-slate-500" />
                    </div>
                    <input
                        type="text"
                        placeholder="Buscar por nome ou categoria..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full bg-slate-800 border border-slate-700 text-white text-sm rounded-lg pl-9 pr-3 py-2 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-colors placeholder:text-slate-500"
                    />
                </div>
            )}

            <div className="space-y-4 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                {sortedCategories.length === 0 ? (
                    <p className="text-xs text-slate-500 italic">Nenhum personagem encontrado.</p>
                ) : (
                    sortedCategories.map(category => (
                        <div key={category} className="space-y-2">
                            <h4 className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">{category}</h4>
                            <div className="flex flex-wrap gap-2">
                                {groupedCharacters[category].map(char => {
                                    const isSelected = selectedIds.includes(char.id);
                                    
                                    let buttonClass = "";
                                    if (mode === 'insert') {
                                        buttonClass = "px-3 py-1.5 rounded-full text-xs font-medium bg-slate-800 text-slate-300 border border-slate-700 hover:bg-emerald-600 hover:text-white hover:border-emerald-500 transition-all";
                                    } else {
                                        buttonClass = `px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${
                                            isSelected
                                            ? 'bg-emerald-600 text-white border-emerald-500 shadow-lg shadow-emerald-900/20'
                                            : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
                                        }`;
                                    }

                                    return (
                                        <button
                                            key={char.id}
                                            onClick={() => onSelect(char)}
                                            className={buttonClass}
                                        >
                                            {char.name}
                                        </button>
                                    );
                                })}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default CharacterSelector;
