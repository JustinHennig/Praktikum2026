import { useState } from "react";

const API = "http://localhost:8000";

export default function Dashboard() {
  const [frequency, setFrequency] = useState(1000);
  const [amplitude, setAmplitude] = useState(1);
  const [measuring, setMeasuring] = useState(false);
  const [results, setResults] = useState<{
    frequency: string;
    amplitude: string;
  } | null>(null);

  const startMeasurement = async () => {
    setMeasuring(true);
    setResults(null);
    try {
      const res = await fetch(`${API}/measure`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ frequency, amplitude }),
      });
      const data = await res.json();
      setResults({ frequency: data.frequency, amplitude: data.amplitude });
    } catch {
      setResults({ frequency: "Fehler", amplitude: "Fehler" });
    } finally {
      setMeasuring(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Messung mit Funktionsgenerator und Oszilloskop</h1>
      </div>

      <div className="card">
        <h2>Signaleinstellungen</h2>
        <div className="form-row">
          <div className="form-group">
            <label>Frequenz (Hz)</label>
            <input
              type="number"
              value={frequency}
              min={0}
              onChange={(e) => setFrequency(Number(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>Amplitude (V)</label>
            <input
              type="number"
              value={amplitude}
              step={0.1}
              min={0}
              onChange={(e) => setAmplitude(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="btn-group">
          <button
            className="btn btn-primary"
            onClick={startMeasurement}
            disabled={measuring}
          >
            {measuring ? "Messung läuft…" : "Messung starten"}
          </button>
        </div>
      </div>

      {results && (
        <div className="card full-width">
          <h2>Messergebnisse</h2>
          <table className="measurement-table">
            <thead>
              <tr>
                <th>Messung</th>
                <th style={{ textAlign: "right" }}>Wert</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Frequenz</td>
                <td className="value">{results.frequency} Hz</td>
              </tr>
              <tr>
                <td>Amplitude</td>
                <td className="value">{results.amplitude} V</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
