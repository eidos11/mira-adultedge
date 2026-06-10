%% false_dilemma.pl — Feature-based verification rules (v1.0.1)
%% Input: flat feature list from LLM Step 2 extraction
%% Called via: verify(false_dilemma, Features, Result) from pattern_verify.pl

:- multifile verified/2.
:- multifile rejected/2.

%% F1 (Walton pragmatic false dilemma): a third option that is merely *dismissed*
%% still verifies — the speaker collapsed the real option space. Only a genuinely
%% *viable* middle (viable_middle_exists(true)) defeats the pattern. The collapse
%% may be implicit, so logical_space_explored is no longer required to verify.
verified(false_dilemma, F) :-
    member(option_count(N), F), N =< 2,
    member(exclusivity_markers(M), F), M \= [],
    member(viable_middle_exists(false), F).

rejected(false_dilemma, F) :-
    member(viable_middle_exists(true), F).
rejected(false_dilemma, F) :-
    member(option_count(N), F), N > 2.
