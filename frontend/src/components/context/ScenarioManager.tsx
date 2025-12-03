'use client';

import { type FC, useState } from 'react';
import { BookmarkPlus, Trash2, FolderOpen, Bookmark } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useContextStore } from '@/stores/contextStore';

export const ScenarioManager: FC = () => {
  const { savedScenarios, saveScenario, loadScenario, deleteScenario } = useContextStore();
  const [newScenarioName, setNewScenarioName] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleSave = () => {
    if (newScenarioName.trim()) {
      saveScenario(newScenarioName.trim());
      setNewScenarioName('');
      setIsAdding(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSave();
    } else if (e.key === 'Escape') {
      setIsAdding(false);
      setNewScenarioName('');
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bookmark className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-semibold">Saved Scenarios</h3>
        </div>
        {!isAdding && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsAdding(true)}
            className="h-7 text-xs"
          >
            <BookmarkPlus className="h-3 w-3 mr-1" />
            Save
          </Button>
        )}
      </div>

      {/* Add New Scenario */}
      {isAdding && (
        <div className="flex gap-2">
          <Input
            placeholder="Scenario name..."
            value={newScenarioName}
            onChange={(e) => setNewScenarioName(e.target.value)}
            onKeyDown={handleKeyDown}
            className="h-8 text-sm"
            autoFocus
          />
          <Button size="sm" onClick={handleSave} className="h-8">
            Save
          </Button>
          <Button
            size="sm"
            variant="ghost"
            onClick={() => {
              setIsAdding(false);
              setNewScenarioName('');
            }}
            className="h-8"
          >
            Cancel
          </Button>
        </div>
      )}

      {/* Saved Scenarios List */}
      {savedScenarios.length === 0 ? (
        <p className="text-xs text-muted-foreground text-center py-2">
          No saved scenarios yet
        </p>
      ) : (
        <div className="space-y-1 max-h-40 overflow-y-auto">
          {savedScenarios.map((scenario) => (
            <div
              key={scenario.id}
              className="flex items-center justify-between p-2 rounded-md bg-muted/50 hover:bg-muted transition-colors group"
            >
              <button
                onClick={() => loadScenario(scenario.id)}
                className="flex items-center gap-2 flex-1 text-left"
              >
                <FolderOpen className="h-3 w-3 text-muted-foreground" />
                <span className="text-sm truncate">{scenario.name}</span>
              </button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteScenario(scenario.id)}
                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <Trash2 className="h-3 w-3 text-destructive" />
              </Button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

