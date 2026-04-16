import React from 'react';
import { Check, Loader, Circle } from 'lucide-react';
import './AgentProgress.css';

const AGENTS = [
  { id: 'preferensi', name: 'Agen Preferensi', desc: 'Menganalisis kebutuhan Anda' },
  { id: 'destinasi', name: 'Agen Destinasi', desc: 'Mencari lokasi terbaik' },
  { id: 'itinerary', name: 'Agen Itinerary', desc: 'Menyusun jadwal perjalanan' },
  { id: 'ringkasan', name: 'Agen Ringkasan', desc: 'Merangkum rekomendasi' },
];

const AgentProgress = ({ activeAgent = null, completedAgents = [] }) => {
  const getStatus = (agentId) => {
    if (completedAgents.includes(agentId)) return 'done';
    if (activeAgent === agentId) return 'active';
    return 'idle';
  };

  return (
    <div className="agent-progress">
      <div className="agent-progress-header">
        <span className="agent-progress-label">STATUS AGEN</span>
      </div>
      <div className="agent-progress-list">
        {AGENTS.map((agent, idx) => {
          const status = getStatus(agent.id);
          return (
            <div key={agent.id} className={`agent-item agent-item-${status}`}>
              <div className="agent-icon-wrapper">
                {status === 'done' && (
                  <div className="agent-icon agent-icon-done">
                    <Check size={12} strokeWidth={3} />
                  </div>
                )}
                {status === 'active' && (
                  <div className="agent-icon agent-icon-active">
                    <Loader size={12} className="animate-spin" />
                  </div>
                )}
                {status === 'idle' && (
                  <div className="agent-icon agent-icon-idle">
                    <Circle size={8} />
                  </div>
                )}
                {idx < AGENTS.length - 1 && (
                  <div className={`agent-connector ${status === 'done' ? 'agent-connector-done' : ''}`}></div>
                )}
              </div>
              <div className="agent-info">
                <span className="agent-name">{agent.name}</span>
                <span className="agent-desc">{agent.desc}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AgentProgress;
