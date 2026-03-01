import { Link } from "react-router-dom";

const cards = [
  {
    title: "Doctor",
    desc: "Register, login, and manage patient notes with digital signatures and timings.",
    register: "/doctor/register",
    login: "/doctor/login",
    color: "from-blue-500/10 via-blue-500/5 to-transparent",
  },
  {
    title: "Patient",
    desc: "Keep your symptoms, upload purchase proofs, and see doctor advice in one place.",
    register: "/patient/register",
    login: "/patient/login",
    color: "from-emerald-500/10 via-emerald-500/5 to-transparent",
  },
  {
    title: "Admin",
    desc: "Simple panel to review doctors and patients before approvals.",
    register: null,
    login: "/admin/login",
    color: "from-amber-500/10 via-amber-500/5 to-transparent",
  },
];

export default function Landing() {
  return (
    <div className="space-y-8">
      <section className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 md:p-8">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <p className="text-xs uppercase tracking-[0.25em] text-primary font-semibold">Starter Pack</p>
            <h1 className="text-3xl md:text-4xl font-bold leading-tight">Prescripto</h1>
            <p className="text-slate-600 text-base">
              A no-frills, beginner-style setup so you can extend for real clinics. Doctors, patients, and admins each
              get their own corner.
            </p>
            <div className="flex gap-3 flex-wrap">
              <Link className="px-4 py-2 rounded-lg bg-primary text-white text-sm shadow" to="/doctor/register">
                Get Started as Doctor
              </Link>
              <Link className="px-4 py-2 rounded-lg border border-slate-300 text-sm" to="/patient/register">
                I&apos;m a Patient
              </Link>
            </div>
          </div>
          <div className="flex-1 grid grid-cols-2 gap-3 text-sm text-slate-700">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs text-slate-500">Doctor Dashboard</p>
              <p className="font-semibold">Notes, timings, advice</p>
              <p className="mt-1 text-slate-500">Digital signature ready</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs text-slate-500">Patient Dashboard</p>
              <p className="font-semibold">Receipts & proofs</p>
              <p className="mt-1 text-slate-500">Upload + view prescriptions</p>
            </div>
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 col-span-2">
              <p className="text-xs text-slate-500">Admin</p>
              <p className="font-semibold">See doctor & patient lists in one glance.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        {cards.map((card) => (
          <div
            key={card.title}
            className={`rounded-2xl border border-slate-200 bg-gradient-to-br ${card.color} p-5 shadow-sm flex flex-col justify-between`}
          >
            <div className="space-y-2">
              <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">{card.title}</div>
              <div className="text-lg font-semibold">{card.title === "Admin" ? "Control Room" : `${card.title} Portal`}</div>
              <p className="text-sm text-slate-600">{card.desc}</p>
            </div>
            <div className="flex gap-2 pt-3">
              {card.register && (
                <Link className="px-3 py-2 rounded-lg bg-primary text-white text-xs" to={card.register}>
                  Register
                </Link>
              )}
              <Link className="px-3 py-2 rounded-lg border border-slate-300 text-xs" to={card.login}>
                Login
              </Link>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}
