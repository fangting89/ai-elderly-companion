import { createFileRoute } from '@tanstack/react-router'
import {
  HeartHandshake,
  Phone,
  ShieldAlert,
  PillBottle,
  TriangleAlert,
} from 'lucide-react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { FamilyShell, MetricCard } from '@/components/FamilyShell'

export const Route = createFileRoute('/family/')({
  head: () => ({
    meta: [
      { title: 'Family view — You Little Companion' },
      {
        name: 'description',
        content:
          'A weekly plain-language summary of how Ma is doing, with alerts only when something genuinely matters.',
      },
    ],
  }),
  component: FamilyDashboard,
})

const adherence = [
  { day: 'Mon', taken: 3, planned: 3 },
  { day: 'Tue', taken: 3, planned: 3 },
  { day: 'Wed', taken: 2, planned: 3 },
  { day: 'Thu', taken: 3, planned: 3 },
  { day: 'Fri', taken: 3, planned: 3 },
  { day: 'Sat', taken: 3, planned: 3 },
  { day: 'Sun', taken: 3, planned: 3 },
]

const moodLabels = ['', 'Low', 'Quiet', 'Steady', 'Warm', 'Bright']
const mood = [
  { day: 'Mon', score: 4 },
  { day: 'Tue', score: 4 },
  { day: 'Wed', score: 3 },
  { day: 'Thu', score: 3 },
  { day: 'Fri', score: 4 },
  { day: 'Sat', score: 5 },
  { day: 'Sun', score: 4 },
]

const alerts = [
  {
    id: 'a1',
    tone: 'caution' as const,
    icon: ShieldAlert,
    title: 'Ma checked a suspicious SMS on Tuesday, and did the right thing.',
    body: 'A message pretending to be from DBS asked her to click a link. She photographed it instead of replying, and it was deleted. Nothing was shared. No action needed from you — you may just want to tell her she handled it well.',
    when: 'Tuesday, 2:41 PM',
  },
  {
    id: 'a2',
    tone: 'calm' as const,
    icon: PillBottle,
    title: 'One evening dose of eye drops was missed on Wednesday.',
    body: "She marked the morning and afternoon doses as taken. This is the first missed dose in three weeks, so it's most likely just a busy evening rather than a pattern. We'll flag it again only if it repeats.",
    when: 'Wednesday, 10:15 PM',
  },
]

function ChartFrame({ children }: { children: React.ReactNode }) {
  return (
    <div className="mt-4 h-48 w-full">
      <ResponsiveContainer width="100%" height="100%">
        {children as React.ReactElement}
      </ResponsiveContainer>
    </div>
  )
}

function FamilyDashboard() {
  return (
    <FamilyShell
      title="How Ma is doing"
      intro="A quiet weekly picture, written the way you'd want a sibling to tell you. We only raise something when it genuinely matters — no live tracking, no minute-by-minute reporting."
    >
      <section className="mb-6 rounded-2xl border-2 border-caution bg-caution/30 p-5 shadow-soft">
        <div className="flex items-start gap-3">
          <TriangleAlert
            className="mt-0.5 size-5 shrink-0"
            aria-hidden="true"
          />
          <p className="text-sm leading-relaxed">
            <strong>
              This is an AI impression of her week, not a diagnosis.
            </strong>{' '}
            It can miss things, misread a quiet mood, or get details wrong. If
            you're genuinely worried about her, the only way to really know how
            she's doing is to call or visit — please don't let a "steady"
            summary here stand in for that.
          </p>
        </div>
      </section>

      <section className="rounded-2xl border border-border bg-card p-6 shadow-soft">
        <h2 className="text-sm font-semibold tracking-wide text-muted-foreground uppercase">
          This week, in a sentence or two
        </h2>
        <p className="mt-3 max-w-3xl leading-relaxed">
          Mdm Tan had a steady week. She mentioned a sore knee on Thursday
          morning — worth a gentle ask, though she didn't seem worried about it.
          She spoke about her Chinatown days more than usual, which she tends to
          do when she's in good spirits. She missed one evening dose of eye
          drops on Wednesday, and caught a scam SMS on Tuesday without replying
          to it.
        </p>
        <p className="mt-4 text-sm text-muted-foreground">
          Written from her own conversations. She knows the summary is shared
          with you.
        </p>
      </section>

      <section className="mt-6">
        <h2 className="text-sm font-semibold tracking-wide text-muted-foreground uppercase">
          Worth knowing
        </h2>
        <ul className="mt-3 flex flex-col gap-3">
          {alerts.map((alert) => (
            <li
              key={alert.id}
              className={[
                'rounded-2xl border p-5',
                alert.tone === 'caution'
                  ? 'border-caution bg-caution/30'
                  : 'border-border bg-card',
              ].join(' ')}
            >
              <div className="flex items-start gap-3">
                <alert.icon
                  className="mt-0.5 size-5 shrink-0"
                  aria-hidden="true"
                />
                <div className="min-w-0">
                  <p className="font-semibold">{alert.title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                    {alert.body}
                  </p>
                  <p className="mt-2 text-xs text-muted-foreground">
                    {alert.when}
                  </p>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </section>

      <div className="mt-6 grid gap-5 lg:grid-cols-2">
        <MetricCard
          label="Medication taken"
          value="20 of 21 doses"
          meaning="Counts the doses she marked as taken this week. One skipped dose is normal and isn't a cause for concern on its own — we'd only call it a pattern after several in a row."
        >
          <ChartFrame>
            <BarChart
              data={adherence}
              margin={{ top: 12, right: 4, left: -24, bottom: 0 }}
            >
              <CartesianGrid vertical={false} stroke="var(--color-border)" />
              <XAxis
                dataKey="day"
                tickLine={false}
                axisLine={false}
                fontSize={12}
              />
              <YAxis
                domain={[0, 3]}
                ticks={[0, 1, 2, 3]}
                tickLine={false}
                axisLine={false}
                fontSize={12}
              />
              <Tooltip
                cursor={{ fill: 'var(--color-secondary)' }}
                contentStyle={{
                  borderRadius: 12,
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-card)',
                }}
                formatter={(value: number) => [`${value} of 3 doses`, 'Taken']}
              />
              <Bar
                isAnimationActive={false}
                dataKey="taken"
                fill="var(--color-chart-1)"
                radius={[8, 8, 4, 4]}
              />
            </BarChart>
          </ChartFrame>
        </MetricCard>

        <MetricCard
          label="How she's seemed"
          value="Steady, with a bright Saturday"
          meaning="A rough read of tone in conversation, described in words rather than a score. It's an impression, not a diagnosis, and a quieter day usually just means a quieter day."
        >
          <ChartFrame>
            <LineChart
              data={mood}
              margin={{ top: 12, right: 8, left: 4, bottom: 0 }}
            >
              <CartesianGrid vertical={false} stroke="var(--color-border)" />
              <XAxis
                dataKey="day"
                tickLine={false}
                axisLine={false}
                fontSize={12}
              />
              <YAxis
                domain={[1, 5]}
                ticks={[1, 2, 3, 4, 5]}
                width={58}
                tickLine={false}
                axisLine={false}
                fontSize={12}
                tickFormatter={(value: number) => moodLabels[value]}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: 12,
                  border: '1px solid var(--color-border)',
                  background: 'var(--color-card)',
                }}
                formatter={(value: number) => [moodLabels[value], 'Seemed']}
              />
              <Line
                isAnimationActive={false}
                type="monotone"
                dataKey="score"
                stroke="var(--color-chart-2)"
                strokeWidth={3}
                dot={{ r: 4, fill: 'var(--color-chart-2)' }}
              />
            </LineChart>
          </ChartFrame>
        </MetricCard>

        <MetricCard
          label="Repeated questions"
          value="0 this week"
          meaning="Zero means she didn't repeat the same question within a short window — this is a genuine reading, not missing data. If we ever have no data at all, this panel will say 'not enough conversation yet' instead of zero."
        >
          <div className="mt-4 flex items-center gap-2 rounded-xl border border-border bg-calm/50 px-4 py-3 text-sm text-calm-foreground">
            <HeartHandshake className="size-4 shrink-0" aria-hidden="true" />
            Measured across 34 conversations this week.
          </div>
        </MetricCard>

        <MetricCard
          label="Connections with family"
          value="4 this week"
          meaning="Times a real conversation happened between Ma and someone in the family — calls she made, notes you sent, and a visit on Sunday. We count human contact, not how long she spent on the app."
        >
          <ul className="mt-4 flex flex-col gap-2 text-sm">
            {[
              { who: 'Call with Wei Ling', when: 'Monday', icon: Phone },
              {
                who: 'Note from Kok Wai',
                when: 'Tuesday',
                icon: HeartHandshake,
              },
              { who: 'Call with Wei Ling', when: 'Friday', icon: Phone },
              {
                who: 'Sunday lunch visit',
                when: 'Sunday',
                icon: HeartHandshake,
              },
            ].map((item) => (
              <li
                key={`${item.who}-${item.when}`}
                className="flex items-center justify-between gap-3 rounded-xl border border-border px-4 py-2"
              >
                <span className="inline-flex min-w-0 items-center gap-2">
                  <item.icon className="size-4 shrink-0" aria-hidden="true" />
                  <span className="truncate">{item.who}</span>
                </span>
                <span className="shrink-0 text-muted-foreground">
                  {item.when}
                </span>
              </li>
            ))}
          </ul>
        </MetricCard>
      </div>

      <p className="mt-8 max-w-2xl text-sm leading-relaxed text-muted-foreground">
        The companion never replaces you. It keeps her company between your
        visits, and nudges her towards picking up the phone — this page exists
        so you can be present without hovering.
      </p>
    </FamilyShell>
  )
}
