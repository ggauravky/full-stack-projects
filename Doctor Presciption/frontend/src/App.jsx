import { useMemo, useState } from "react";
import { Link, Route, Routes, useLocation, useNavigate } from "react-router-dom";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

const demoDoctors = [
  {
    id: 1,
    name: "Dr. Siya Rao",
    email: "doc@prescripto.com",
    password: "doctor123",
    specialty: "General Physician",
    timing: "Mon-Sat | 10:00 AM - 4:00 PM",
    bio: "Checks fever, cold, and routine consults. Friendly and quick.",
    signature: "Dr. Siya (digital)",
  },
];

const demoPatients = [
  {
    id: 1,
    name: "Rahul Singh",
    email: "rahul@demo.com",
    password: "patient123",
    age: 28,
    symptoms: "Headache, mild fever",
    appointmentTime: "02:30 PM",
    advice: "Drink water every 30 mins, take rest",
    notes: "Follow up in 3 days",
    proof: "receipt-123.png",
    photo: "profile.png",
  },
];

const PageShell = ({ children }) => {
  const location = useLocation();
  const simpleTitle = useMemo(() => {
    if (location.pathname === "/") return "Prescripto";
    return location.pathname.replace("/", "").replaceAll("-", " ");
  }, [location.pathname]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-indigo-50 to-slate-100 text-slate-800">
      <header className="bg-white/90 backdrop-blur shadow-sm sticky top-0 z-10 border-b border-slate-100">
        <div className="max-w-6xl mx-auto flex items-center justify-between px-4 py-3">
          <Link to="/" className="flex items-center gap-2 text-xl font-semibold text-primary">
            <span className="h-9 w-9 rounded-xl bg-primary/10 text-primary grid place-items-center text-sm font-bold">Rx</span>
            Prescripto
          </Link>
          <nav className="flex gap-2 text-sm">
            <Link className="nav-btn" to="/">Home</Link>
            <Link className="nav-btn" to="/doctor/login">Doctor</Link>
            <Link className="nav-btn" to="/patient/login">Patient</Link>
            <Link className="nav-btn" to="/admin/login">Admin</Link>
          </nav>
        </div>
      </header>
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-5 text-xs uppercase tracking-[0.25em] text-slate-500">{simpleTitle}</div>
        {children}
      </main>
    </div>
  );
};

const Landing = () => (
  <div className="grid gap-8">
    <div className="section shadow-md bg-gradient-to-br from-white via-slate-50 to-indigo-50">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
        <div className="space-y-4 max-w-2xl">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white border border-slate-200 shadow-sm text-xs font-semibold text-primary">
            MediCare · Professional onboarding
          </div>
          <h1 className="text-4xl font-bold leading-tight text-slate-900">
            Join the future of professional healthcare management.
          </h1>
          <p className="text-slate-600 text-lg">
            Capture complete doctor credentials, connect patients fast, and keep admins aligned — all in one simple starter.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link className="btn-primary" to="/doctor/register">Start Doctor Intake</Link>
            <Link className="btn-secondary" to="/patient/register">Patient Intake</Link>
            <Link className="btn-ghost" to="/admin/login">Admin Login</Link>
          </div>
          <div className="flex flex-wrap gap-3 text-sm text-slate-600">
            <span className="badge">Identity + credentials</span>
            <span className="badge">Hospital details</span>
            <span className="badge">Secure handoff</span>
          </div>
        </div>
        <div className="w-full md:w-80 bg-white border border-slate-100 rounded-2xl shadow-sm p-5 space-y-3">
          <p className="text-sm font-semibold text-primary">Choose a portal</p>
          <div className="space-y-2">
            <Link to="/doctor/register" className="block list-card hover:border-primary/50 hover:shadow transition">
              <p className="font-semibold text-slate-900">Doctor Intake</p>
              <p className="text-sm text-slate-600">Capture credentials, hospital info, timings, signatures.</p>
            </Link>
            <Link to="/patient/register" className="block list-card hover:border-primary/50 hover:shadow transition">
              <p className="font-semibold text-slate-900">Patient Intake</p>
              <p className="text-sm text-slate-600">Register, upload proofs, track doctor advice.</p>
            </Link>
            <Link to="/admin/login" className="block list-card hover:border-primary/50 hover:shadow transition">
              <p className="font-semibold text-slate-900">Admin Panel</p>
              <p className="text-sm text-slate-600">See doctor + patient lists with quick status.</p>
            </Link>
          </div>
          <p className="text-xs text-slate-500">Click any action above to continue.</p>
        </div>
      </div>
    </div>
  </div>
);

const DoctorRegister = ({ onCreate }) => {
  const [form, setForm] = useState({
    firstName: "",
    middleName: "",
    lastName: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
    specialty: "",
    experience: "",
    hospital: "",
    hospitalPhone: "",
    license: "",
    address: "",
    timing: "",
    bio: "",
    signature: "",
  });
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    if (!form.firstName || !form.lastName || !form.username || !form.email || !form.password || !form.confirmPassword) {
      return alert("Please fill all required fields");
    }
    if (form.password !== form.confirmPassword) return alert("Passwords do not match");
    onCreate({
      ...form,
      name: `${form.firstName} ${form.middleName ? form.middleName + " " : ""}${form.lastName}`,
      id: Date.now(),
    });
    navigate("/doctor/dashboard");
  };

  return (
    <div className="section">
      <div className="section-head">
        <h2 className="section-title">Doctor Register</h2>
        <p className="section-hint">Capture full identity and credentials for professional onboarding.</p>
      </div>
      <form onSubmit={submit} className="form-grid">
        <label className="form-field">
          <span>First Name*</span>
          <input className="input" placeholder="John" value={form.firstName} onChange={(e) => setForm({ ...form, firstName: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Middle Name</span>
          <input className="input" placeholder="Quincy" value={form.middleName} onChange={(e) => setForm({ ...form, middleName: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Last Name*</span>
          <input className="input" placeholder="Doe" value={form.lastName} onChange={(e) => setForm({ ...form, lastName: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Username*</span>
          <input className="input" placeholder="john_doe" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Email Address*</span>
          <input className="input" placeholder="john@hospital.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Phone Number</span>
          <input className="input" placeholder="+1 (555) 000-0000" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Password*</span>
          <input className="input" type="password" placeholder="••••••" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Confirm Password*</span>
          <input className="input" type="password" placeholder="••••••" value={form.confirmPassword} onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Specialization*</span>
          <input className="input" placeholder="Neurologist" value={form.specialty} onChange={(e) => setForm({ ...form, specialty: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Experience (Years)*</span>
          <input className="input" placeholder="8" value={form.experience} onChange={(e) => setForm({ ...form, experience: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Hospital / Clinic Name*</span>
          <input className="input" placeholder="City General Hospital" value={form.hospital} onChange={(e) => setForm({ ...form, hospital: e.target.value })} />
        </label>
        <label className="form-field md:col-span-2">
          <span>Hospital Address*</span>
          <input className="input" placeholder="Full street address..." value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Hospital Phone*</span>
          <input className="input" placeholder="Office contact" value={form.hospitalPhone} onChange={(e) => setForm({ ...form, hospitalPhone: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Medical License Number*</span>
          <input className="input" placeholder="MD-12345678" value={form.license} onChange={(e) => setForm({ ...form, license: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Available time</span>
          <input className="input" placeholder="11 AM - 3 PM" value={form.timing} onChange={(e) => setForm({ ...form, timing: e.target.value })} />
        </label>
        <label className="form-field md:col-span-2">
          <span>Short bio / advice</span>
          <textarea className="input h-24" placeholder="Quick intro or default advice" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Digital signature text</span>
          <input className="input" placeholder="Dr. Siya" value={form.signature} onChange={(e) => setForm({ ...form, signature: e.target.value })} />
        </label>
        <div className="md:col-span-2 flex gap-3">
          <button className="btn-primary" type="submit">Save &amp; dashboard</button>
          <p className="text-xs text-slate-500">Demo: doc@prescripto.com / doctor123</p>
        </div>
      </form>
    </div>
  );
};

const DoctorLogin = ({ doctors, onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    const ok = onLogin(email, password);
    if (ok) navigate("/doctor/dashboard");
    else alert("No doctor found. Try demo: doc@prescripto.com / doctor123");
  };

  return (
    <div className="section max-w-md">
      <div className="section-head">
        <h2 className="section-title">Doctor Login</h2>
        <p className="section-hint">Quick check-in to manage your patients.</p>
      </div>
      <form onSubmit={submit} className="form-grid">
        <label className="form-field">
          <span>Email</span>
          <input className="input" placeholder="doc@prescripto.com" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="form-field">
          <span>Password</span>
          <input className="input" type="password" placeholder="••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button className="btn-primary" type="submit">Login</button>
        <p className="text-xs text-slate-500">Demo: doc@prescripto.com / doctor123</p>
      </form>
    </div>
  );
};

const DoctorDashboard = ({ doctor, patients, updateDoctor }) => {
  const [note, setNote] = useState(doctor?.bio || "");
  const [signature, setSignature] = useState(doctor?.signature || "");

  if (!doctor) return <div className="section">Login first to see your dashboard.</div>;

  const save = () => {
    updateDoctor({ ...doctor, bio: note, signature });
    alert("Saved basic details");
  };

  return (
    <div className="grid md:grid-cols-3 gap-6">
      <div className="section md:col-span-1">
        <h3 className="section-title">Doctor Profile</h3>
        <p className="font-semibold text-primary mt-1">{doctor.name}</p>
        <p className="text-sm text-slate-500">{doctor.specialty || "Specialty not set"}</p>
        <p className="text-sm mt-2">{doctor.timing || "Timing not set"}</p>
        <textarea className="input h-24 mt-4" value={note} onChange={(e) => setNote(e.target.value)} placeholder="Description / advice" />
        <input className="input mt-2" value={signature} onChange={(e) => setSignature(e.target.value)} placeholder="Digital signature" />
        <button className="btn-primary mt-3 w-full" onClick={save}>Save Description</button>
      </div>
      <div className="section md:col-span-2">
        <div className="flex items-center justify-between mb-4">
          <h3 className="section-title">Patients under you</h3>
          <span className="badge">{patients.length} total</span>
        </div>
        <div className="space-y-3">
          {patients.map((p) => (
            <div key={p.id} className="list-card">
              <div className="flex justify-between text-sm">
                <div className="font-semibold text-slate-800">{p.name}</div>
                <div className="text-slate-500">{p.appointmentTime}</div>
              </div>
              <p className="text-slate-600 text-sm">Symptoms: {p.symptoms}</p>
              <p className="text-sm text-primary">Advice: {p.advice}</p>
              <p className="text-xs text-slate-500">Proof: {p.proof || "none"}</p>
            </div>
          ))}
          {!patients.length && <p className="text-sm text-slate-500">No patients yet.</p>}
        </div>
      </div>
    </div>
  );
};

const PatientRegister = ({ onCreate }) => {
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    age: "",
    symptoms: "",
    appointmentTime: "",
    advice: "",
    proof: "",
    photo: "",
  });
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    if (!form.name || !form.email || !form.password) return alert("Fill name/email/password");
    onCreate({ ...form, id: Date.now(), age: Number(form.age || 0) });
    navigate("/patient/dashboard");
  };

  return (
    <div className="section">
      <div className="section-head">
        <h2 className="section-title">Patient Register</h2>
        <p className="section-hint">Capture basics plus quick uploads for receipts and proofs.</p>
      </div>
      <form onSubmit={submit} className="form-grid">
        <label className="form-field">
          <span>Full name *</span>
          <input className="input" placeholder="Rahul Singh" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Email *</span>
          <input className="input" placeholder="rahul@demo.com" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Password *</span>
          <input className="input" type="password" placeholder="••••••" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Age</span>
          <input className="input" placeholder="28" value={form.age} onChange={(e) => setForm({ ...form, age: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Symptoms</span>
          <input className="input" placeholder="Headache, mild fever" value={form.symptoms} onChange={(e) => setForm({ ...form, symptoms: e.target.value })} />
        </label>
        <label className="form-field">
          <span>Appointment time</span>
          <input className="input" placeholder="02:30 PM" value={form.appointmentTime} onChange={(e) => setForm({ ...form, appointmentTime: e.target.value })} />
        </label>
        <label className="form-field md:col-span-2">
          <span>Doctor advice (optional)</span>
          <textarea className="input h-20" placeholder="Take rest, etc." value={form.advice} onChange={(e) => setForm({ ...form, advice: e.target.value })} />
        </label>
        <div className="grid grid-cols-2 gap-3 md:col-span-2">
          <label className="form-field">
            <span>Upload photo</span>
            <input className="input" type="file" onChange={(e) => setForm({ ...form, photo: e.target.files?.[0]?.name || "" })} />
          </label>
          <label className="form-field">
            <span>Receipt / proof</span>
            <input className="input" type="file" onChange={(e) => setForm({ ...form, proof: e.target.files?.[0]?.name || "" })} />
          </label>
        </div>
        <div className="md:col-span-2 flex gap-3 items-center">
          <button className="btn-primary" type="submit">Save Patient</button>
          <p className="text-xs text-slate-500">Demo: rahul@demo.com / patient123</p>
        </div>
      </form>
    </div>
  );
};

const PatientLogin = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    const ok = onLogin(email, password);
    if (ok) navigate("/patient/dashboard");
    else alert("Not found. Try demo: rahul@demo.com / patient123");
  };

  return (
    <div className="section max-w-md">
      <div className="section-head">
        <h2 className="section-title">Patient Login</h2>
        <p className="section-hint">View your uploads and doctor advice.</p>
      </div>
      <form onSubmit={submit} className="form-grid">
        <label className="form-field">
          <span>Email</span>
          <input className="input" placeholder="rahul@demo.com" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="form-field">
          <span>Password</span>
          <input className="input" type="password" placeholder="••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button className="btn-primary" type="submit">Login</button>
        <p className="text-xs text-slate-500">Demo: rahul@demo.com / patient123</p>
      </form>
    </div>
  );
};

const PatientDashboard = ({ patient, updatePatient }) => {
  const [local, setLocal] = useState(patient);

  if (!patient) return <div className="section">Login to view patient dashboard.</div>;

  const save = () => {
    updatePatient(local);
    alert("Patient updated");
  };

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="section">
        <h3 className="section-title">Patient Profile</h3>
        <input className="input mt-3" value={local.name} onChange={(e) => setLocal({ ...local, name: e.target.value })} />
        <input className="input mt-2" value={local.symptoms} onChange={(e) => setLocal({ ...local, symptoms: e.target.value })} />
        <input className="input mt-2" value={local.appointmentTime} onChange={(e) => setLocal({ ...local, appointmentTime: e.target.value })} />
        <textarea className="input h-20 mt-2" value={local.advice} onChange={(e) => setLocal({ ...local, advice: e.target.value })} />
        <div className="grid grid-cols-2 gap-3 mt-3">
          <label className="text-xs text-slate-500">
            Upload photo
            <input className="input mt-1" type="file" onChange={(e) => setLocal({ ...local, photo: e.target.files?.[0]?.name || "" })} />
          </label>
          <label className="text-xs text-slate-500">
            Receipt / proof
            <input className="input mt-1" type="file" onChange={(e) => setLocal({ ...local, proof: e.target.files?.[0]?.name || "" })} />
          </label>
        </div>
        <button className="btn-primary w-full mt-3" onClick={save}>Save</button>
      </div>
      <div className="section">
        <h3 className="section-title">Quick Summary</h3>
        <p className="text-sm text-slate-600 mt-2">Advice: {local.advice || "No advice yet"}</p>
        <p className="text-sm text-slate-600">Photo: {local.photo || "not uploaded"}</p>
        <p className="text-sm text-slate-600">Proof: {local.proof || "not uploaded"}</p>
        <p className="text-sm text-slate-600">Next visit: {local.notes || "soon"}</p>
      </div>
    </div>
  );
};

const AdminLogin = ({ onLogin }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const submit = (e) => {
    e.preventDefault();
    const ok = onLogin(email, password);
    if (ok) navigate("/admin/dashboard");
    else alert("Try admin@prescripto.com / admin123");
  };

  return (
    <div className="section max-w-md">
      <div className="section-head">
        <h2 className="section-title">Admin Login</h2>
        <p className="section-hint">Check doctor and patient lists in one glance.</p>
      </div>
      <form onSubmit={submit} className="form-grid">
        <label className="form-field">
          <span>Admin email</span>
          <input className="input" placeholder="admin@prescripto.com" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="form-field">
          <span>Password</span>
          <input className="input" type="password" placeholder="••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        <button className="btn-primary" type="submit">Login as Admin</button>
        <p className="text-xs text-slate-500">Demo: admin@prescripto.com / admin123</p>
      </form>
    </div>
  );
};

const AdminDashboard = ({ doctors, patients }) => (
  <div className="grid md:grid-cols-2 gap-6">
    <div className="section">
      <div className="flex items-center justify-between mb-3">
        <h3 className="section-title">Doctors</h3>
        <span className="badge">{doctors.length}</span>
      </div>
      <div className="space-y-2">
        {doctors.map((d) => (
          <div key={d.id} className="list-card">
            <div className="font-semibold">{d.name}</div>
            <div className="text-xs text-slate-500">{d.email}</div>
            <div className="text-sm text-primary">{d.specialty || "Not set"}</div>
          </div>
        ))}
        {!doctors.length && <p className="text-sm text-slate-500">No doctors yet.</p>}
      </div>
    </div>
    <div className="section">
      <div className="flex items-center justify-between mb-3">
        <h3 className="section-title">Patients</h3>
        <span className="badge">{patients.length}</span>
      </div>
      <div className="space-y-2">
        {patients.map((p) => (
          <div key={p.id} className="list-card">
            <div className="font-semibold">{p.name}</div>
            <div className="text-xs text-slate-500">{p.email}</div>
            <div className="text-sm text-slate-600">Symptoms: {p.symptoms}</div>
          </div>
        ))}
        {!patients.length && <p className="text-sm text-slate-500">No patients yet.</p>}
      </div>
    </div>
  </div>
);

function App() {
  const [doctors, setDoctors] = useState(demoDoctors);
  const [patients, setPatients] = useState(demoPatients);
  const [activeDoctor, setActiveDoctor] = useState(demoDoctors[0]);
  const [activePatient, setActivePatient] = useState(demoPatients[0]);
  const [admin, setAdmin] = useState(false);

  const sendToApi = async (path, payload) => {
    try {
      await fetch(`${API_URL}${path}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (err) {
      console.log("API offline, continuing with local data only", err.message);
    }
  };

  const doctorLogin = (email, password) => {
    const found = doctors.find((d) => d.email === email && d.password === password);
    setActiveDoctor(found || null);
    return Boolean(found);
  };

  const patientLogin = (email, password) => {
    const found = patients.find((p) => p.email === email && p.password === password);
    setActivePatient(found || null);
    return Boolean(found);
  };

  const adminLogin = (email, password) => {
    if (email === "admin@prescripto.com" && password === "admin123") {
      setAdmin(true);
      return true;
    }
    return false;
  };

  const addDoctor = (doc) => {
    setDoctors((prev) => [...prev, doc]);
    setActiveDoctor(doc);
    sendToApi("/api/doctor/register", doc);
  };

  const addPatient = (pat) => {
    setPatients((prev) => [...prev, pat]);
    setActivePatient(pat);
    sendToApi("/api/patient/register", pat);
  };

  const updateDoctor = (doc) => {
    setDoctors((prev) => prev.map((d) => (d.id === doc.id ? doc : d)));
    setActiveDoctor(doc);
  };

  const updatePatient = (pat) => {
    setPatients((prev) => prev.map((p) => (p.id === pat.id ? pat : p)));
    setActivePatient(pat);
  };

  return (
    <PageShell>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/doctor/register" element={<DoctorRegister onCreate={addDoctor} />} />
        <Route path="/doctor/login" element={<DoctorLogin doctors={doctors} onLogin={doctorLogin} />} />
        <Route path="/doctor/dashboard" element={<DoctorDashboard doctor={activeDoctor} patients={patients} updateDoctor={updateDoctor} />} />

        <Route path="/patient/register" element={<PatientRegister onCreate={addPatient} />} />
        <Route path="/patient/login" element={<PatientLogin onLogin={patientLogin} />} />
        <Route path="/patient/dashboard" element={<PatientDashboard patient={activePatient} updatePatient={updatePatient} />} />

        <Route path="/admin/login" element={<AdminLogin onLogin={adminLogin} />} />
        <Route path="/admin/dashboard" element={admin ? <AdminDashboard doctors={doctors} patients={patients} /> : <div className="section">Please login as admin.</div>} />
      </Routes>
    </PageShell>
  );
}

export default App;
