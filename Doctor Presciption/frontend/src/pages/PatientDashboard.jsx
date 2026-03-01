import { useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:4000";

export default function PatientDashboard() {
  const saved = JSON.parse(localStorage.getItem("patient_user") || "{}");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [upload, setUpload] = useState({ receiptPhoto: "", proofOfPurchase: "" });
  const [message, setMessage] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const id = saved.id || "pat-1";
        const res = await fetch(`${API_BASE}/api/patient/${id}/dashboard`);
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

  const handleUpload = async (e) => {
    e.preventDefault();
    try {
      const id = saved.id || "pat-1";
      const res = await fetch(`${API_BASE}/api/patient/${id}/uploads`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(upload),
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.error || "Upload failed");
      setMessage("Files saved (just storing links in this starter)");
      setData((prev) => ({
        ...prev,
        uploads: {
          receiptPhoto: upload.receiptPhoto || prev?.uploads?.receiptPhoto,
          proofOfPurchase: upload.proofOfPurchase || prev?.uploads?.proofOfPurchase,
        },
      }));
    } catch (err) {
      setMessage(err.message);
    }
  };

  if (loading) return <p>Loading patient dashboard...</p>;
  if (!data) return <p>Could not load data.</p>;

  return (
    <div className="space-y-4">
      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <p className="text-xs uppercase tracking-[0.25em] text-primary font-semibold">Patient Dashboard</p>
        <h2 className="text-2xl font-bold mt-1">{data.name}</h2>
        <p className="text-sm text-slate-600">{data.email}</p>
        <p className="text-sm text-slate-500 mt-2">Diagnosis: {data.diagnosis || "Not set"}</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 space-y-3">
          <h3 className="font-semibold">Uploaded Proofs</h3>
          <div className="grid gap-2 text-sm text-slate-700">
            <div>
              <p className="text-xs text-slate-500">Receipt Photo</p>
              <img src={data.uploads?.receiptPhoto || "https://placehold.co/320x180?text=Receipt"} alt="Receipt" className="rounded-lg border" />
            </div>
            <div>
              <p className="text-xs text-slate-500">Proof of Purchase</p>
              <img src={data.uploads?.proofOfPurchase || "https://placehold.co/320x180?text=Proof"} alt="Proof" className="rounded-lg border" />
            </div>
          </div>
        </div>

        <form className="bg-white border border-slate-200 rounded-2xl shadow-sm p-4 space-y-3" onSubmit={handleUpload}>
          <h3 className="font-semibold">Upload / paste links</h3>
          <label className="grid gap-1 text-sm">
            <span className="text-slate-700">Receipt Photo URL</span>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              name="receiptPhoto"
              value={upload.receiptPhoto}
              onChange={(e) => setUpload((p) => ({ ...p, receiptPhoto: e.target.value }))}
              placeholder="https://..."
            />
          </label>
          <label className="grid gap-1 text-sm">
            <span className="text-slate-700">Proof of Purchase URL</span>
            <input
              className="w-full rounded-lg border border-slate-300 px-3 py-2"
              name="proofOfPurchase"
              value={upload.proofOfPurchase}
              onChange={(e) => setUpload((p) => ({ ...p, proofOfPurchase: e.target.value }))}
              placeholder="https://..."
            />
          </label>
          <button className="px-4 py-2 rounded-lg bg-primary text-white text-sm shadow" type="submit">
            Save Uploads
          </button>
          {message && <p className="text-xs text-slate-600">{message}</p>}
        </form>
      </div>
    </div>
  );
}
