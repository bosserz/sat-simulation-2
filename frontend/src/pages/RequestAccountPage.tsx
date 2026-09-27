import { Link } from "react-router-dom";

export function RequestAccountPage() {
  return (
    <div className="mx-auto max-w-2xl rounded-md border border-slate-200 bg-white p-6 shadow-soft">
      <h1 className="text-2xl font-bold">Request Account</h1>
      <p className="mt-3 text-slate-600">
        Please contact your Intsight Education administrator to create or activate your practice account.
      </p>
      <Link to="/login" className="secondary-button mt-6 inline-flex">Back to login</Link>
    </div>
  );
}
