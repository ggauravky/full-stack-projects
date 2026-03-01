import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:4000";

export default function DoctorDashboard() {
  const saved = JSON.parse(localStorage.getItem("doctor_user") || "{}");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const id = saved.id || "doc-1";
        const res = await fetch(`${API_BASE}/api/doctor/${id}/dashboard`);
        const payload = await res.json();
        setData(payload);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [saved.id]);

  if (loading) return <p>Loading doctor dashboard...</p>;
  if (!data) return <p>Could not load data.</p>;

  return (
    <div className="space-y-4">
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.25em] text-primary font-semibold">Doctor Dashboard</p>
            <h2 className="text-2xl font-bold mt-1">{data.name}</h2>
            <p className="text-slate-600 text-sm">{data.speciality || "General Physician"}</p>
            <p className="text-sm text-slate-500 mt-2">{data.timings || "Timings not set"}</p>
          </div>
          {data.signature && (
            <img src={data.signature} alt="signature" className="h-12 w-auto object-contain" />
          )}
        </div>
        <div className="mt-4 grid gap-3 md:grid-cols-3 text-sm text-slate-700">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-xs text-slate-500">Default Advice</p>
            <p className="font-semibold">{data.advice || "Add some advice"}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-xs text-slate-500">Symptoms</p>
            <p className="font-semibold">{data.symptoms || "Headache, Fever"}</p>
          </div>
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
            <p className="text-xs text-slate-500">Patients Assigned</p>
            <p className="font-semibold">{data.patients?.length || 2}</p>
          </div>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Recent Advice Notes</h3>
          <span className="text-xs text-slate-500">sample data</span>
        </div>
        <div className="space-y-3">
          {(data.notes || []).map((note, idx) => (
            <div key={idx} className="p-3 border border-slate-200 rounded-lg bg-slate-50">
              <div className="flex items-center justify-between text-sm">
                <span className="font-semibold text-slate-800">{note.patient}</span>
                <span className="text-xs text-slate-500">Advice #{idx + 1}</span>
              </div>
              <p className="text-sm text-slate-700 mt-1">{note.advice}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
