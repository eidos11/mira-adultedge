%% oversimplified_cause.pl — Feature-based verification rules (v1.0.1)
%% Input: flat feature list from LLM Step 2 extraction
%% Called via: verify(oversimplified_cause, Features, Result) from pattern_verify.pl

:- multifile verified/2.
:- multifile rejected/2.

verified(oversimplified_cause, F) :-
    member(cause_count(N), F), N =:= 1,
    member(alternative_causes_mentioned(false), F),
    member(sufficiency_claim_strength(strong), F),
    member(causal_claim_type(T), F), T \= physical_direct.

rejected(oversimplified_cause, F) :-
    member(cause_count(N), F), N > 1.
rejected(oversimplified_cause, F) :-
    member(alternative_causes_mentioned(true), F).
