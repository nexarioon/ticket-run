# Third-party playbook stacks

An agent-style stack (playbook packs that route tasks to playbooks — shipping tails,
autopilot loops, adversarial review panels) can be installed alongside this kit. It does not
replace the pipeline; bind it to this order.

## The binding rules

1. **The gate wins.** Test plan, then coding plan, then code. A playbook that jumps straight
   to architecture and delegation may run only inside Stages 3–4, after the matrices exist.
2. **Never let a playbook reach its shipping tail** — opening a PR, shipping, babysit,
   autopilot — unless the user asked for push/PR/merge by name. Those steps push, force-push
   and squash-merge.
3. **A stack in another profile has none of this kit's enforcement** and none of your
   project memory. Paste the gate rules into the prompt there, or run the gate here and hand
   the approved plan over.
4. **Translate port instructions instead of obeying them verbatim.** Another harness's tool
   names, isolation flags, and model slugs may not exist in yours. Leave model roles unset so
   subagents inherit the session model.

## Which skills of such a stack are safe at which stage

| Stage | Safe to borrow | Never |
|---|---|---|
| 1 Intake | goal-restating, prompt-sharpening | delegation fan-out |
| 2 Test plan | adversarial review of the matrices | generating expected values from thin air |
| 3 Coding plan | parallel design exploration, blast-radius listing | skipping the plan approval gate |
| 4 Implementation | root-cause discipline, smallest-change rules | autopilot loops, force-push |
| 5 Verification | adversarial diff review, benchmark checklists, state charts | weakening the predicate |
| 6 Report | prose de-slopping, evidence tables | claiming green from a run not executed |

## Surveying a stack cheaply

Read its manifest and the playbook that matches your task class before installing anything.
Look for three tells: does any playbook end in a push/merge step; does any playbook relax a
check to declare victory; do its model defaults name models your provider does not have.
Those three answers decide how much of the stack is safe to keep.
