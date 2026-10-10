import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from 'recharts';
import client from '../api/client';
import Navbar from '../components/Navbar';
import KpiCard from '../components/KpiCard';

interface SubjectStat {
  subject_name: string;
  subject_code: string;
  average_marks: number;
  pass_count: number;
  fail_count: number;
  max_marks: number;
}

interface AdminData {
  total_students: number;
  total_subjects: number;
  overall_pass_rate: number;
  subject_stats: SubjectStat[];
}

interface Student {
  id: number;
  name: string;
  roll_number: string;
  department: string;
  year: number;
}

const PIE_COLORS = ['#22c55e', '#ef4444'];

export default function AdminDashboard() {
  const [data, setData] = useState<AdminData | null>(null);
  const [students, setStudents] = useState<Student[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function load() {
      try {
        const [dashRes, studRes] = await Promise.all([
          client.get('/dashboard/admin'),
          client.get('/students'),
        ]);
        setData(dashRes.data);
        setStudents(studRes.data);
      } catch {
        setError('Failed to load dashboard data.');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="flex items-center justify-center min-h-screen text-gray-500">Loading...</div>;
  if (error) return <div className="flex items-center justify-center min-h-screen text-red-500">{error}</div>;
  if (!data) return null;

  const pieData = [
    { name: 'Pass', value: data.subject_stats.reduce((s, x) => s + x.pass_count, 0) },
    { name: 'Fail', value: data.subject_stats.reduce((s, x) => s + x.fail_count, 0) },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar title="Admin Dashboard — Academic Performance" />

      <div className="max-w-7xl mx-auto px-6 py-6 space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard label="Total Students" value={data.total_students} color="bg-blue-50 border-blue-200" />
          <KpiCard label="Total Subjects" value={data.total_subjects} color="bg-purple-50 border-purple-200" />
          <KpiCard label="Overall Pass Rate" value={`${data.overall_pass_rate}%`} color="bg-green-50 border-green-200" />
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Bar Chart — avg marks per subject */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
            <h2 className="text-sm font-semibold text-gray-600 mb-4">Average Marks per Subject</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.subject_stats} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="subject_code" angle={-30} textAnchor="end" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v) => [`${v}`, 'Avg Marks']} />
                <Bar dataKey="average_marks" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Pie Chart — pass vs fail */}
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
            <h2 className="text-sm font-semibold text-gray-600 mb-4">Pass vs Fail Distribution</h2>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} cx="50%" cy="45%" outerRadius={85} dataKey="value" label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`} labelLine={false}>
                  {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                </Pie>
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Per-Subject Stats Table */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-600 mb-4">Subject Performance Breakdown</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 pr-4 font-medium">Subject</th>
                  <th className="pb-2 pr-4 font-medium">Code</th>
                  <th className="pb-2 pr-4 font-medium">Avg Marks</th>
                  <th className="pb-2 pr-4 font-medium">Max Marks</th>
                  <th className="pb-2 pr-4 font-medium">Pass</th>
                  <th className="pb-2 font-medium">Fail</th>
                </tr>
              </thead>
              <tbody>
                {data.subject_stats.map((s) => (
                  <tr key={s.subject_code} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-medium text-gray-800">{s.subject_name}</td>
                    <td className="py-2 pr-4 text-gray-500">{s.subject_code}</td>
                    <td className="py-2 pr-4">{s.average_marks}</td>
                    <td className="py-2 pr-4 text-gray-500">{s.max_marks}</td>
                    <td className="py-2 pr-4 text-green-600 font-medium">{s.pass_count}</td>
                    <td className="py-2 text-red-500 font-medium">{s.fail_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Students Table */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-600 mb-4">All Students</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="pb-2 pr-4 font-medium">Name</th>
                  <th className="pb-2 pr-4 font-medium">Roll No.</th>
                  <th className="pb-2 pr-4 font-medium">Department</th>
                  <th className="pb-2 font-medium">Year</th>
                </tr>
              </thead>
              <tbody>
                {students.map((s) => (
                  <tr key={s.id} className="border-b border-gray-50 hover:bg-gray-50">
                    <td className="py-2 pr-4 font-medium text-gray-800">{s.name}</td>
                    <td className="py-2 pr-4 text-gray-500">{s.roll_number}</td>
                    <td className="py-2 pr-4">{s.department}</td>
                    <td className="py-2">{s.year}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

