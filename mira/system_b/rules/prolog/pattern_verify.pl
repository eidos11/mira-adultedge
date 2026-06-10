%% pattern_verify.pl — Common 3-valued verification engine
%% v1.0.1 Lane 2 Bridge
%%
%% Verdict priority: reject > accept > unverified.
%% If both verified/2 and rejected/2 match, reject wins —
%% conservative approach aligned with "first, do no harm" coaching.

:- multifile verified/2.
:- multifile rejected/2.
:- discontiguous verified/2.
:- discontiguous rejected/2.

verify(Pattern, Features, Result) :-
    ( rejected(Pattern, Features) -> Result = reject
    ; verified(Pattern, Features) -> Result = accept
    ; Result = unverified
    ).
