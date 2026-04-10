// app.js
import React, { useState, useEffect } from 'react';
import { Leaf, Zap, Loader2, AlertTriangle, CheckCircle } from 'lucide-react';

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/dashboard');
        if (response.ok) {
          const result = await response.json();
          setData(result); // No frontend logic — Edge decides everything
        }
      } catch (err) {
        console.error("Link to Belden Brain lost...");
        setData({ edge_status: false });
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  if (!data) {
    return (
      <div style={{
        backgroundColor: '#0f172a',
        height: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: '#38bdf8',
        flexDirection: 'column'
      }}>
        <Loader2 size={48} style={{ animation: 'spin 2s linear infinite' }} />
        <h2 style={{ marginTop: '20px', letterSpacing: '2px' }}>
          CONNECTING TO BELDEN HORIZON...
        </h2>
        <style>{`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  return (
    <div style={{
      backgroundColor: '#0f172a',
      minHeight: '100vh',
      color: 'white',
      padding: '40px',
      fontFamily: 'sans-serif'
    }}>

      {/* EDGE STATUS INDICATOR */}
      <div style={{
        backgroundColor: data.edge_status ? '#065f46' : '#7f1d1d',
        color: data.edge_status ? '#a3f7bf' : '#fecaca',
        padding: '8px 16px',
        borderRadius: '8px',
        marginBottom: '20px',
        display: 'inline-flex',
        alignItems: 'center',
        gap: '8px'
      }}>
        {data.edge_status ? <CheckCircle size={16} /> : <AlertTriangle size={16} />}
        Edge Gateway: {data.edge_status ? "ONLINE" : "OFFLINE"}
      </div>

      {/* HEADER */}
      <header style={{
        display: 'flex',
        justifyContent: 'space-between',
        borderBottom: '1px solid #334155',
        paddingBottom: '20px',
        marginBottom: '30px'
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '24px' }}>
            BELDEN <span style={{ color: '#38bdf8' }}>HORIZON</span>
          </h1>
          <p style={{ color: '#94a3b8' }}>
            {data.rack_id} • AI Insight Engine
          </p>
        </div>

        <div style={{
          backgroundColor: '#064e3b',
          padding: '10px 20px',
          borderRadius: '8px',
          textAlign: 'right'
        }}>
          <span style={{
            color: '#34d399',
            fontSize: '11px',
            fontWeight: 'bold'
          }}>
            PREVENTED DOWNTIME
          </span>
          <h2 style={{ margin: 0 }}>
            ${data.insights?.roi_saved_usd || "0"}
          </h2>
        </div>
      </header>

      <div style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '25px'
      }}>

        {/* CONNECTIVITY MATRIX */}
        <section style={{
          backgroundColor: '#1e293b',
          padding: '25px',
          borderRadius: '16px'
        }}>
          <h3>Connectivity Matrix</h3>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, 1fr)',
            gap: '15px',
            marginTop: '20px'
          }}>
            {data.ports?.map((port) => (
              <div
                key={port.id}
                style={{
                  padding: '15px',
                  borderRadius: '12px',
                  backgroundColor: '#0f172a',
                  textAlign: 'center',
                  border: `2px solid ${
                    port.status === 'Healthy' ? '#059669' :
                    port.status === 'Warning' ? '#facc15' :
                    '#dc2626'
                  }`
                }}
              >
                <p style={{ fontSize: '10px', color: '#94a3b8' }}>
                  PORT {port.id}
                </p>

                <div style={{ fontWeight: 'bold' }}>
                  {port.errors} ERRORS
                </div>

                {port.status === "Critical" && (
                  <div style={{
                    color: '#dc2626',
                    fontSize: '12px',
                    marginTop: '5px'
                  }}>
                    <AlertTriangle size={16} /> CRITICAL
                  </div>
                )}
              </div>
            ))}
          </div>

          <p style={{
            color: '#f87171',
            marginTop: '15px',
            fontWeight: 'bold'
          }}>
            Total Errors: {data.total_errors || 0}
          </p>
        </section>

        {/* SUSTAINABILITY */}
        <section style={{
          display: 'flex',
          flexDirection: 'column',
          gap: '20px'
        }}>

          <div style={{
            background: 'linear-gradient(135deg, #064e3b 0%, #065f46 100%)',
            padding: '25px',
            borderRadius: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '15px'
            }}>
              <Leaf size={24} />
              <h3 style={{ margin: 0 }}>Sustainability</h3>
            </div>

            <p>
              Carbon: <strong>
                {data.sustainability?.carbon_footprint_kg} kg CO₂
              </strong>
            </p>

            <p>
              Status: <strong>
                {data.sustainability?.scope_3_status}
              </strong>
            </p>
          </div>

          <div style={{
            backgroundColor: '#1e293b',
            padding: '25px',
            borderRadius: '16px'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              marginBottom: '10px'
            }}>
              <Zap size={24} color="#f1c40f" />
              <h3 style={{ margin: 0 }}>Energy Waste</h3>
            </div>

            <p>
              {data.sustainability?.energy_waste_kwh} kWh / Loss
            </p>
          </div>

          {/* AI Recommendation */}
          <div style={{
            backgroundColor: '#0f172a',
            padding: '20px',
            borderRadius: '12px',
            border: '1px solid #334155'
          }}>
            <h4 style={{ marginBottom: '8px' }}>AI Recommendation</h4>
            <p style={{ color: '#94a3b8' }}>
              {data.insights?.ai_recommendation || "Analyzing system..."}
            </p>
          </div>

        </section>
      </div>
    </div>
  );
}
import HealthChart from "./HealthChart";

function App() {
  return (
    <div>
      <h1>Belden Cable Monitoring</h1>
      <HealthChart />
    </div>
  );
}


export default App;