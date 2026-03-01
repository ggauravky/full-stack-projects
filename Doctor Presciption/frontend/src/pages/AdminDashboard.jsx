import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:4000";

export default function AdminDashboard() {
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [dRes, pRes] = await Promise.all([
          fetch(`${API_BASE}/api/admin/doctors`),
          fetch(`${API_BASE}/api/admin/patients`),
        ]);
        setDoctors(await dRes.json());
        setPatients(await pRes.json());
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  if (loading) return <p>Loading admin dashboard...</p>;

  return (
    <div className="grid md:grid-cols-2 gap-4">
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Doctors</h3>
          <span className="text-xs text-slate-500">{doctors.length} total</span>
        </div>
        <div className="space-y-2 text-sm">
          {doctors.map((doc) => (
            <div key={doc.id || doc.email} className="p-3 border border-slate-200 rounded-lg bg-slate-50">
              <div className="font-semibold text-slate-800">{doc.name || "Unknown Doctor"}</div>
              <div className="text-slate-600">{doc.email}</div>
              <div className="text-xs text-slate-500">{doc.speciality || "Speciality not set"}</div>
            </div>
          ))}
          {doctors.length === 0 && <p className="text-slate-500">No doctors yet.</p>}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Patients</h3>
          <span className="text-xs text-slate-500">{patients.length} total</span>
        </div>
        <div className="space-y-2 text-sm">
          {patients.map((pat) => (
            <div key={pat.id || pat.email} className="p-3 border border-slate-200 rounded-lg bg-slate-50">
              <div className="font-semibold text-slate-800">{pat.name || "Unknown Patient"}</div>
              <div className="text-slate-600">{pat.email}</div>
              <div className="text-xs text-slate-500">Doctor: {pat.doctorId || "not linked"}</div>
            </div>
          ))}
          {patients.length === 0 && <p className="text-slate-500">No patients yet.</p>}
        </div>
      </div>
    </div>
  );
}
