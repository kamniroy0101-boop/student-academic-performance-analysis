import { useEffect, useState } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts';
import client from '../api/client';
import Navbar from '../components/Navbar';
import KpiCard from '../components/KpiCard';
import { useAuth } from '../context/useAuth';

interface GradeRow {
  grade_id: number;
  subject_name: string;
  subject_code: string;
  exam_type: string;
  marks_obtained: number;
  max_marks: number;
  semester: string;
  passed: boolean;
}

interface ChartPoint {
  subject_name: string;
  marks_obtained: number;
  max_marks: number;
}

interface StudentData {
  student_name: string;
  roll_number: string;
  department: string;
  year: number;
  subjects_enrolled: number;
  overall_average: number;
  highest_subject: string | null;
  subject_chart_data: ChartPoint[];
  grades: GradeRow[];
}

export default function StudentDashboard() {
  const { user } = useAuth();
  const [data, setData] = useState<StudentData | null>(null);
  const [fetchError, setFetchError] = useState('');
  const [fetched, setFetched] = useState(false);

  const missingProfile = !user?.student_id;

  useEffect(() => {
    if (missingProfile) return;
    client.get(`/dashboard/student/${user.student_id}`)
      .then((r) => setData(r.data))
      .catch(() => setFetchError('Failed to load your dashboard.'))
      .finally(() => setFetched(true));
  }, [user, missingProfile]);

  const error = missingProfile ? 'Student profile not found for this account.' : fetchError;
  const loading = !missingProfile && !fetched;

  if (loading) return <div className="flex items-center justify-center min-h-screen text-gray-500">Loading...</div>;
  if (error) return <div className="flex items-center justify-center min-h-screen text-red-500">{error}</div>;
  if (!data) return null;

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar title={`My Dashboard — ${data.student_name}`} />

      <div className="max-w-5xl mx-auto px-6 py-6 space-y-6">
        {/* Student Info Banner */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm px-5 py-4 flex flex-wrap gap-4 text-sm text-gray-600">
          <span><strong>Roll No:</strong> {data.roll_number}</span>
          <span><strong>Department:</strong> {data.department}</span>
          <span><strong>Year:</strong> {data.year}</span>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <KpiCard label="Subjects Enrolled" value={data.subjects_enrolled} color="bg-blue-50 border-blue-200" />
          <KpiCard label="Overall Average" value={`${data.overall_average}%`} color="bg-purple-50 border-purple-200" />
          <KpiCard label="Best Subject" value={data.highest_subject ?? '—'} color="bg-green-50 border-green-200" />
        </div>

        {/* Bar Chart — obtained vs max marks */}
        {data.subject_chart_data.length > 0 && (
          <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
            <h2 className="text-sm font-semibold text-gray-600 mb-4">Marks Obtained vs Max Marks</h2>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={data.subject_chart_data} margin={{ top: 5, right: 10, left: 0, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="subject_name" angle={-25} textAnchor="end" tick={{ fontSize: 11 }} />
                <YAxis tick={{ fontSize: 11 }} />
                <Tooltip />
                <Legend verticalAlign="top" />
                <Bar dataKey="marks_obtained" name="Obtained" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="max_marks" name="Max" fill="#e5e7eb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Grades Table */}
        <div className="bg-white rounded-2xl border border-gray-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-gray-600 mb-4">My Grades</h2>
          {data.grades.length === 0 ? (
            <p className="text-sm text-gray-400">No grades recorded yet.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-gray-500 border-b">
                    <th className="pb-2 pr-4 font-medium">Subject</th>
                    <th className="pb-2 pr-4 font-medium">Exam Type</th>
                    <th className="pb-2 pr-4 font-medium">Semester</th>
                    <th className="pb-2 pr-4 font-medium">Marks</th>
                    <th className="pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {data.grades.map((g) => (
                    <tr key={g.grade_id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-2 pr-4 font-medium text-gray-800">{g.subject_name}</td>
                      <td className="py-2 pr-4 capitalize text-gray-600">{g.exam_type}</td>
                      <td className="py-2 pr-4 text-gray-500">{g.semester}</td>
                      <td className="py-2 pr-4">{g.marks_obtained} / {g.max_marks}</td>
                      <td className="py-2">
                        <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${g.passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                          {g.passed ? 'Pass' : 'Fail'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

