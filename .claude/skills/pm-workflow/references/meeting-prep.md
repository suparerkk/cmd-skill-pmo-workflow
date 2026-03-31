# Meeting Prep — Client Meeting Question Preparation

Prepares PMs with tailored, prioritized question lists before client meetings. Generates domain-aware questions with reasoning and red flags.

## When to Use

User says:
- "I have a client meeting about X"
- "help me prep for the X meeting"
- "what should I ask about X"
- "prepare questions for X discussion"
- "I'm meeting with <company> about X"
- "I need questions ready for tomorrow's X meeting"

---

## Behavior

### 1. Gather Context

Before generating questions, ask these **context-gathering questions** (one at a time, conversationally):

```
"Before I generate questions — quick context:
- What type of meeting? (discovery, pitch, check-in, roadmap review, kickoff)
- Who's in the room? (executives, engineers, end users, external stakeholders)
- What do you already know about the project?
- What's at stake? (budget decision, timeline commitment, relationship milestone)
- Any constraints or pressure points you're aware of?"
```

**How to ask:**
- Ask all at once in a single message
- Accept partial answers (PM may not know everything)
- Don't block if PM skips some — use what's provided
- If user provides context in their initial message, skip gathering

---

### 2. Run Optional PM Skills

Based on the context gathered, run relevant skills to sharpen the meeting prep. These are **optional** — skip if the user wants quick prep or context is too thin.

**Note:** These skills are best-effort in meeting prep context. They normally run with full project context (requirements, personas, etc.), but during meeting prep that context may not exist yet. The skills will produce lighter output — that's fine. The goal is to sharpen questions, not produce complete artifacts.

#### Company Research (if company name is provided)

If the user mentions a company name (e.g., "meeting with Acme Corp"), run:

```
Run: /company-research
```

Use the research brief to:
- Tailor questions to the company's product strategy and org structure
- Reference specific executive quotes or recent moves in questions
- Identify competitive landscape to ask sharper positioning questions

**Skip if:** No company name provided, or user says "just give me generic questions."

#### Discovery Interview Prep (for discovery or kickoff meetings)

If the meeting type is **discovery** or **kickoff**, run:

```
Run: /discovery-interview-prep
```

Use the interview plan to:
- Structure questions around a clear learning goal
- Ensure questions target the right customer segment
- Add methodological rigor (avoid leading questions, ensure open-ended framing)

**Skip if:** Meeting type is check-in, status, or roadmap review.

#### Jobs to Be Done (for discovery meetings)

If the meeting type is **discovery** and the topic involves understanding user needs, run:

```
Run: /jobs-to-be-done
```

Use the JTBD output to:
- Frame "Must Ask" questions around customer jobs, pains, and gains
- Replace generic feature questions with "When <situation>, what do you need to accomplish?" style
- Identify hiring/firing criteria for the product

**Skip if:** Meeting is not discovery-focused, or the topic is purely technical (e.g., migration, infrastructure).

---

### 3. Determine Meeting Type

Route question generation based on meeting type:

#### Discovery Meeting
**Goal:** Understand the problem, users, and constraints.
**Focus areas:** Problem space, user pain points, success criteria, constraints, existing systems.

#### Pitch / Proposal Meeting
**Goal:** Validate assumptions, scope the engagement.
**Focus areas:** Budget alignment, timeline expectations, decision criteria, competition.

#### Check-in / Status Meeting
**Goal:** Realign on progress, unblock issues.
**Focus areas:** Progress blockers, scope changes, timeline risks, stakeholder feedback.

#### Roadmap Review
**Goal:** Align on priorities and timeline.
**Focus areas:** Priority shifts, market changes, resource constraints, upcoming milestones.

#### Kickoff Meeting
**Goal:** Align team on scope, roles, and plan.
**Focus areas:** Roles & responsibilities, communication cadence, risk awareness, definition of done.

---

### 4. Generate Tiered Questions

Generate **10-15 questions** organized in three tiers. Incorporate insights from any PM skills run in Step 2 — company research sharpens context, discovery interview prep structures the approach, and JTBD reframes questions around customer jobs.

#### Must Ask (Deal-Breakers) — 3-5 questions

Questions that uncover fundamental risks. Without answers to these, you can't scope the work.

Format per question:
```markdown
**Q: "<question text>"**
- **Why:** <what this reveals, why it matters>
- **Red flags:** <what answers should concern you>
- **Follow-up if vague:** "<probing question>"
```

#### Should Ask (Scope-Shapers) — 4-6 questions

Questions that determine scope, priority, and approach. Answers shape the PRD.

Same format as Must Ask.

#### Nice to Ask (Clarity-Improvers) — 3-4 questions

Questions that add depth and reduce ambiguity. Lower priority but valuable.

Same format as Must Ask.

---

### 5. Add Domain-Specific Questions

Based on the project domain, inject relevant technical questions:

| Domain | Sample Topics |
|--------|--------------|
| SaaS product | Pricing model, multi-tenancy, onboarding flow, churn triggers |
| API / Platform | Rate limits, auth model, SLA requirements, versioning strategy |
| Mobile app | Offline support, push permissions, app store requirements, device targets |
| Integration / Migration | Legacy systems, data mapping, cutover strategy, rollback plan |
| Enterprise software | SSO/compliance, approval workflows, audit trails, org hierarchy |
| Consumer product | User acquisition, retention metrics, viral loops, monetization |

**Detection:** Infer domain from context (what user says they're building). If unclear, ask.

---

### 6. Generate Meeting Prep File

Save the output to `.pm/meeting-prep-<topic>.md`:

```markdown
---
name: <topic>
meeting_type: discovery | pitch | check-in | roadmap | kickoff
created: <ISO 8601>
attendees: <who's in the room>
company: <client name if provided>
---

# Meeting Prep: <Topic>

**Date:** <meeting date if provided>
**Type:** <meeting type>
**Attendees:** <who's in the room>
**Prepared by:** PM

---

## Meeting Goal
<1-2 sentences on what this meeting should achieve>

---

## Must Ask (Deal-Breakers)

**Q: "<question 1>"**
- **Why:** <reason>
- **Red flags:** <warning signs>
- **Follow-up if vague:** "<probing question>"

**Q: "<question 2>"**
...

---

## Should Ask (Scope-Shapers)

**Q: "<question 4>"**
- **Why:** <reason>
- **Red flags:** <warning signs>
- **Follow-up if vague:** "<probing question>"

...

---

## Nice to Ask (Clarity-Improvers)

**Q: "<question 8>"**
...

---

## After the Meeting

- [ ] Capture answers in meeting notes
- [ ] Identify new questions that came up
- [ ] Update `.pm/context.md` with key decisions
- [ ] If ready to start discovery: "I want to build <topic>"
```

---

### 7. Append to Audit Log

```json
{"timestamp":"2026-03-30T10:00:00Z","phase":0,"action":"meeting_prep","topic":"notification-system","meeting_type":"discovery","artifacts_created":[".pm/meeting-prep-notification-system.md"]}
```

---

## Output

After generating questions:

```
✅ Created meeting prep: .pm/meeting-prep-notification-system.md

📋 12 questions prepared (4 Must Ask, 5 Should Ask, 3 Nice to Ask)

**Tips:**
- Start with Must Ask questions
- If answers are vague, use the follow-up probes
- If answers are specific, move to Should Ask
- Watch for red flags — they change project scope

**After the meeting:**
Say: "I want to build <topic>" to start discovery with your meeting notes
```

---

## Example Session

```
You: "I have a discovery meeting tomorrow with Acme Corp about building a notification system"

Claude: Let me prepare targeted questions for your meeting.

        Quick context:
        - Who's in the room? (e.g., CEO, CTO, product owner)
        - What's the budget range, if you know it?
        - Any existing systems or constraints?
        - What's the timeline expectation?

You: "CTO and VP Product. Budget is $50-100K. They have a legacy email system they want to modernize. Launch by Q2."

Claude: Generating questions for your discovery meeting...

        ## Must Ask (Deal-Breakers)

        **Q: "What happens today when notifications fail to deliver?"**
        - **Why:** Determines reliability requirements and SLA expectations
        - **Red flags:** "We don't know" or "It's not a big deal" — suggests notifications aren't critical, which contradicts the budget
        - **Follow-up if vague:** "Can you walk me through the last time a notification was missed? What was the impact?"

        **Q: "Who manages notification preferences — your admins or their end users?"**
        - **Why:** B2B admin control vs end-user control is fundamentally different scope
        - **Red flags:** Vague answers or conflicting signals from CTO vs VP Product
        - **Follow-up if vague:** "Can you give me a concrete example of how a user changes their notification settings today?"

        **Q: "What's your current notification volume and where do you expect it in 12 months?"**
        - **Why:** Determines infrastructure choice (Firebase vs custom vs third-party)
        - **Red flags:** "We haven't measured" or 10x+ growth expected without budget alignment
        - **Follow-up if vague:** "Can you check your email provider dashboard for daily send volume?"

        **Q: "What's the legacy email system — and why replace it now?"**
        - **Why:** Migration scope depends on what's being replaced and the triggering event
        - **Red flags:** "It works fine but we want something newer" — no real pain, low adoption risk
        - **Follow-up if vague:** "What specific problems are your users reporting with the current system?"

        ---

        ## Should Ask (Scope-Shapers)

        **Q: "Do you need to comply with GDPR, CAN-SPAM, or any regional notification laws?"**
        - **Why:** Legal requirements affect architecture (opt-in tracking, audit logs)
        - **Red flags:** "Not sure" when they have EU customers

        **Q: "Should users see notification history? How far back?"**
        - **Why:** Storage and cost implications scale with retention period
        - **Red flags:** "Forever" without discussing storage costs

        **Q: "What channels beyond push and email are on your radar?"**
        - **Why:** Architecture extensibility — building for SMS/Slack/webhooks later
        - **Red flags:** "All of them" with no prioritization

        **Q: "Who on your team will own this system post-launch?"**
        - **Why:** Long-term maintenance affects tech stack decisions
        - **Red flags:** "We'll figure that out later"

        **Q: "What does success look like in 3 months after launch?"**
        - **Why:** Defines MVP scope and measurement criteria
        - **Red flags:** No measurable criteria

        ---

        ## Nice to Ask (Clarity-Improvers)

        **Q: "What's the fallback if a user has push notifications disabled?"**
        - **Why:** Resilience and degraded experience planning
        - **Red flags:** No fallback plan

        **Q: "Do you need notification templates or is everything dynamic?"**
        - **Why:** CMS complexity vs simple generation
        - **Red flags:** "Both" without prioritization

        **Q: "Any existing analytics or dashboards this needs to integrate with?"**
        - **Why:** Reporting requirements add scope
        - **Red flags:** Multiple integrations mentioned as "easy"

        ---

        ✅ Saved to: .pm/meeting-prep-notification-system.md

        💡 **Tip:** Start with Q1 (failure handling) — it sets the tone for technical depth. If they engage, you're in a good discovery. If they deflect, dig deeper with the follow-up probes.

        **After the meeting:**
        Say: "I want to build the notification system" to start formal discovery
```

---

## Integration Points

### Before This Phase
- No prerequisites — meeting prep can be the very first thing a PM does

### After This Phase
- PM attends meeting with prepared questions
- PM captures answers as meeting notes
- PM says "I want to build X" → routes to `brainstorm.md`
- Brainstorm phase uses meeting prep insights to accelerate discovery

### State Update
Meeting prep does **not** advance the workflow phase. It's a pre-Phase 1 activity.

---

## Transition

User triggers brainstorm (Phase 1) by saying:
- "I want to build X"
- "let's plan X"
- "start discovery on X"

The brainstorm phase should **check for existing meeting prep files**:

```bash
# Check if meeting prep exists
ls .pm/meeting-prep-*.md 2>/dev/null
```

If found, read them and use as context for discovery — don't re-ask questions the PM already answered in the meeting.
