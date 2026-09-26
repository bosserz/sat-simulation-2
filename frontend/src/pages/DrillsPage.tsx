import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import { Loading } from "../components/Loading";

export function DrillsPage() {
  const [topics, setTopics] = useState<Record<string, any[]> | null>(null);

  useEffect(() => {
    api.drillTopics().then((data) => setTopics(data.topics_by_section));
  }, []);

  if (!topics) return <Loading label="Loading drills..." />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Short Drills</h1>
        <p className="mt-1 text-slate-600">Choose a topic and complete a focused practice set.</p>
      </div>
      {Object.entries(topics).map(([section, rows]) => (
        <section className="panel" key={section}>
          <h2 className="section-title capitalize">{section}</h2>
          <div className="grid gap-3 md:grid-cols-2">
            {rows.map((topic: any) => (
              <Link className="row-card hover:border-aqua" key={topic.topic_name} to={`/drill_topic/${encodeURIComponent(topic.topic_name)}`}>
                <div>
                  <p className="font-semibold">{topic.topic_name}</p>
                  <p className="text-sm text-slate-500">{topic.description}</p>
                </div>
                <span className="text-sm font-semibold text-aqua">{topic.completed_sets}/{topic.num_sets}</span>
              </Link>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}
