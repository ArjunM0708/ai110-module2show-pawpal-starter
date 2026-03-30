# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

The initial UML had six classes, the relationships were Owner owns one Pet and many PetTasks → Scheduler consumes an Owner → produces a DailyPlan → composed of ScheduledTasks → each wrapping a PetTask.

- What classes did you include, and what responsibilities did you assign to each?
Six classes, each with a distinct responsibility:

PetTask
Represents a single care task. Its only responsibility is holding task data (title, duration, priority, notes) and validating itself via is_schedulable() it knows whether it's fit to be scheduled.

Pet
A pure data container for the animal. Holds name, species, age, and special needs. No behavior it just exists to be referenced by the owner.

Owner
The central data hub. Responsible for holding the time budget, the pet reference, and the task list. Also responsible for managing that list adding and removing tasks. It does not schedule; it just owns everything the scheduler needs.

Scheduler
The only class with real logic. Solely responsible for taking an owner's data and producing a plan. Internally it delegates to two helpers: one for ranking tasks by priority, one for checking whether a task fits in remaining time.

DailyPlan
The output object. Responsible for holding the results of scheduling — what was scheduled, what was skipped, and the total time used. Also responsible for explaining itself in plain text via explain().

ScheduledTask
A thin wrapper that bridges PetTask and DailyPlan. Responsible for attaching scheduling metadata specifically when a task starts and why it was chosen to an otherwise plain task object.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The original UML put all logic inside classes. During implementation I realized that PRIORITY_ORDER the dict mapping "high", "medium", "low" to numeric weights — was needed by both PetTask.is_schedulable() and Scheduler._rank_tasks(). Rather than duplicate it or arbitrarily own it in one class, we lifted it to module level. _minutes_to_time() followed the same reasoning it's a formatting utility used by DailyPlan.explain() with no natural home in any single class.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The owner's total time budget for the day is the hard constraint. No task is scheduled if it would exceed the remaining minutes. This is enforced in _fits_in_time() and tracked throughout generate_plan() by decrementing remaining after each task is added.
Tasks are ranked high → medium → low before scheduling begins via _rank_tasks(). This ensures higher-priority tasks get first access to the time budget. If time runs out, it's always the lower-priority tasks that get skipped  never the other way around. Priority was based on the scenario in the README.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

 picks tasks in priority order and schedules each one the moment it fits, it never looks ahead. This greedy approach was a good tradeoff since it was predictable and fast.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI mainly for brainstorming, and used it to create the UML diagram, as demonstrated in class before and did a relatively good job at doing so. AI was also incredibly useful for writing test cases. Prompting the AI with test cases were most helpful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

AI thought that the UML diagram would not have been necessary. I disagree, as it was very helpful in visualizing the program. I evaluated AI propositions by asking very specific questions, as to why that particular proposition would work or not.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

PetTask validity tested that is_schedulable() accurately validated acceptable tasks and rejected tasks that were unrecognizable, or of zero duration. The ranking test verified that _rank_tasks() always produced high to medium to low order. 

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am pretty confident that the schedule works correctly, as I've ran the updated PawPal + my self and made sure everything worked according to plan. An edge case that would've been worth looking into is all tasks having the same priority. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with the backend implementation of PawPal+. This is my first time working on something like this.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

Perhaps a more user friendly, updated UI.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One imporant thing I learned is that AI is incredibly useful at writing UML diagrams. This can be very helpful going forward when working on different, more complicated projects, even if a UML diagram isn't necessary.

Demo:

<a href="/course_images/ai110/Screenshot (22).png" target="_blank"><img src='/course_images/ai110/Screenshot (22).png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>
