import { useEffect, useState } from 'react';
import { browseFiles, getRecentFiles } from '../api/client';
import type { FileBrowserResponse, FileNode } from '../types';
import styles from './FileBrowser.module.css';

interface FileBrowserProps {
  selectedFile: FileNode | null;
  onSelectFile: (file: FileNode | null) => void;
}

export function FileBrowser({ selectedFile, onSelectFile }: FileBrowserProps) {
  const [browseMode, setBrowseMode] = useState<'project' | 'system'>('project');
  const [directoryType, setDirectoryType] = useState<'scraped' | 'cards'>('scraped');
  const [currentPath, setCurrentPath] = useState('');
  const [parentPath, setParentPath] = useState<string | null>(null);
  const [nodes, setNodes] = useState<FileNode[]>([]);
  const [recentFiles, setRecentFiles] = useState<FileNode[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load recent files on mount
  useEffect(() => {
    const loadRecent = async () => {
      try {
        const files = await getRecentFiles(10);
        setRecentFiles(files);
      } catch (err) {
        console.error('Failed to load recent files:', err);
      }
    };
    loadRecent();
  }, []);

  // Load directory contents when mode/path changes
  useEffect(() => {
    const loadDirectory = async () => {
      setLoading(true);
      setError(null);
      try {
        const response: FileBrowserResponse = await browseFiles(
          currentPath,
          browseMode,
          directoryType
        );
        setNodes(response.nodes);
        setCurrentPath(response.current_path);
        setParentPath(response.parent_path ?? null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load directory');
        setNodes([]);
      } finally {
        setLoading(false);
      }
    };
    loadDirectory();
  }, [browseMode, directoryType, currentPath]);

  const handleModeChange = (mode: 'project' | 'system') => {
    setBrowseMode(mode);
    setCurrentPath(''); // Reset path when switching modes
    onSelectFile(null); // Clear selection
  };

  const handleDirectoryTypeChange = (type: 'scraped' | 'cards') => {
    setDirectoryType(type);
    setCurrentPath(''); // Reset path when switching directory type
    onSelectFile(null); // Clear selection
  };

  const handleNodeClick = (node: FileNode) => {
    if (!node.readable) {
      setError('Permission denied');
      return;
    }

    if (node.type === 'directory') {
      setCurrentPath(node.path);
      onSelectFile(null); // Clear selection when navigating
    } else {
      onSelectFile(node);
    }
  };

  const handleNavigateUp = () => {
    if (parentPath !== null) {
      setCurrentPath(parentPath);
      onSelectFile(null);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatRelativeTime = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className={styles.container}>
      {/* Browse Mode Selector */}
      <div className={styles.modeSelector}>
        <button
          type="button"
          className={browseMode === 'project' ? styles.modeButtonActive : styles.modeButton}
          onClick={() => handleModeChange('project')}
        >
          Project Files
        </button>
        <button
          type="button"
          className={browseMode === 'system' ? styles.modeButtonActive : styles.modeButton}
          onClick={() => handleModeChange('system')}
        >
          System Files
        </button>
      </div>

      {/* Directory Type Selector (Project mode only) */}
      {browseMode === 'project' && (
        <div className={styles.directoryTypeSelector}>
          <button
            type="button"
            className={directoryType === 'scraped' ? styles.typeButtonActive : styles.typeButton}
            onClick={() => handleDirectoryTypeChange('scraped')}
          >
            Scraped (.md)
          </button>
          <button
            type="button"
            className={directoryType === 'cards' ? styles.typeButtonActive : styles.typeButton}
            onClick={() => handleDirectoryTypeChange('cards')}
          >
            Cards (.json)
          </button>
        </div>
      )}

      {/* Recent Files Panel */}
      {recentFiles.length > 0 && (
        <div className={styles.recentPanel}>
          <h3 className={styles.recentTitle}>Recent Files</h3>
          <div className={styles.recentList}>
            {recentFiles.slice(0, 5).map((file, idx) => (
              <button
                type="button"
                key={idx}
                className={styles.recentItem}
                onClick={() => onSelectFile(file)}
              >
                <span className={styles.recentName}>{file.name}</span>
                <span className={styles.recentTime}>{formatRelativeTime(file.modified)}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Current Path Display */}
      <div className={styles.pathDisplay}>
        <span className={styles.pathLabel}>Current:</span>
        <span className={styles.pathValue}>
          {currentPath || (browseMode === 'project' ? `${directoryType}/` : 'Home')}
        </span>
      </div>

      {/* File Browser */}
      <div className={styles.browserPanel}>
        {loading && <div className={styles.loading}>Loading...</div>}

        {error && <div className={styles.error}>{error}</div>}

        {!loading && !error && (
          <div className={styles.nodeList}>
            {/* Up Navigation */}
            {parentPath !== null && (
              <button type="button" className={styles.nodeItem} onClick={handleNavigateUp}>
                <span className={styles.nodeIcon}>📁</span>
                <span className={styles.nodeName}>..</span>
                <span className={styles.nodeInfo}>Parent directory</span>
              </button>
            )}

            {/* Directory/File List */}
            {nodes.length === 0 && <div className={styles.emptyState}>No files found</div>}

            {nodes.map((node, idx) => (
              <button
                type="button"
                key={idx}
                className={`${styles.nodeItem} ${
                  selectedFile?.path === node.path ? styles.nodeItemSelected : ''
                } ${!node.readable ? styles.nodeItemDisabled : ''}`}
                onClick={() => handleNodeClick(node)}
                disabled={!node.readable}
              >
                <span className={styles.nodeIcon}>{node.type === 'directory' ? '📁' : '📄'}</span>
                <span className={styles.nodeName}>{node.name}</span>
                <span className={styles.nodeInfo}>
                  {node.type === 'file' ? formatFileSize(node.size) : ''}
                  {!node.readable && ' (Permission denied)'}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Selected File Display */}
      {selectedFile && (
        <div className={styles.selectedDisplay}>
          <span className={styles.selectedLabel}>Selected:</span>
          <span className={styles.selectedPath}>{selectedFile.path}</span>
        </div>
      )}
    </div>
  );
}
