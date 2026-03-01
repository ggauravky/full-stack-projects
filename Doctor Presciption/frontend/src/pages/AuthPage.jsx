import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:4000";

const roleLabels = {
  doctor: "Doctor",
  patient: "Patient",
  admin: "Admin",
};

const extraFields = {
  doctor: [
    { name: "speciality", label: "Speciality", placeholder: "Cardiologist" },
    { name: "timings", label: "Available Timings", placeholder: "Mon-Fri, 10am-4pm" },
    { name: "symptoms", label: "Common Symptoms Seen", placeholder: "Chest pain, breathlessness" },
    { name: "advice", label: "Default Advice", placeholder: "Walk 15 mins, drink water" },
    { name: "signature", label: "Digital Signature URL", placeholder: "https://.../sign.png" },
  ],
  patient: [
    { name: "age", label: "Age", placeholder: "26" },
    { name: "symptoms", label: "Symptoms", placeholder: "Cough, mild fever" },
    { name: "receiptPhoto", label: "Receipt Photo URL", placeholder: "https://..." },
    { name: "proofOfPurchase", label: "Proof of Purchase", placeholder: "Invoice #123" },
  ],
};

export default function AuthPage({ role = "doctor", mode = "login" }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ email: "", password: "", name: "" });
  const [status, setStatus] = useState({ type: "", message: "" });
  const [loading, setLoading] = useState(false);

  const title = `${roleLabels[role]} ${mode === "login" ? "Login" : "Register"}`;

  const fields = useMemo(() => {
    if (mode === "login") return [{ name: "email", label: "Email" }, { name: "password", label: "Password", type: "password" }];
    const extras = extraFields[role] || [];
    return [
      { name: "name", label: "Full Name" },
      { name: "email", label: "Email" },
      { name: "password", label: "Password", type: "password" },
      ...extras,
    ];
  }, [mode, role]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (role === "admin" && mode === "register") {
      setStatus({ type: "error", message: "Admins are login-only in this starter." });
      return;
    }
    setLoading(true);
    setStatus({ type: "", message: "" });
    try {
      const endpoint = mode === "register" ? `/api/register/${role}` : `/api/login/${role}`;
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Something went wrong");

      // Save quick session for dashboards
      localStorage.setItem(`${role}_user`, JSON.stringify(data.user || data.data || data));
      setStatus({ type: "success", message: data.message || "Done" });
      if (mode === "login") {
        navigate(`/${role}/dashboard`);
      }
    } catch (err) {
      setStatus({ type: "error", message: err.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-6">
        <p className="text-xs uppercase tracking-[0.25em] text-primary font-semibold">{roleLabels[role]} space</p>
        <h2 className="text-2xl font-bold mt-2">{title}</h2>
        <p className="text-slate-600 text-sm">Beginner friendly form · talks to the Express API at {API_BASE}</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-6">
        <form className="grid gap-4" onSubmit={handleSubmit}>
          {fields.map((field) => (
            <label key={field.name} className="grid gap-1 text-sm">
              <span className="text-slate-700">{field.label}</span>
              <input
                required={mode === "register" || field.name !== "name"}
                name={field.name}
                type={field.type || "text"}
                placeholder={field.placeholder || field.label}
                value={formData[field.name] || ""}
                onChange={handleChange}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </label>
          ))}

          <button
            type="submit"
            disabled={loading}
            className="mt-2 inline-flex justify-center px-4 py-2 rounded-lg bg-primary text-white font-semibold shadow disabled:opacity-70"
          >
            {loading ? "Working..." : title}
          </button>
        </form>

        {status.message && (
          <p className={`mt-4 text-sm ${status.type === "error" ? "text-red-600" : "text-green-600"}`}>
            {status.message}
          </p>
        )}
      </div>

      <div className="mt-6 text-sm text-slate-600 space-y-2">
        <p>Demo credentials:</p>
        <ul className="list-disc list-inside">
          <li>Doctor: aisha@example.com / doctor123</li>
          <li>Patient: ravi@example.com / patient123</li>
          <li>Admin: admin@prescripto.local / admin123</li>
        </ul>
      </div>
    </div>
  );
}
