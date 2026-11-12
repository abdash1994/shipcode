import {EditorState, Compartment} from "@codemirror/state";
import {EditorView, keymap, lineNumbers, drawSelection, highlightActiveLine} from "@codemirror/view";
import {defaultKeymap, history, historyKeymap, indentWithTab} from "@codemirror/commands";
import {syntaxHighlighting, indentUnit, bracketMatching} from "@codemirror/language";
import {classHighlighter} from "@lezer/highlight";
import {python} from "@codemirror/lang-python";
import {sql, SQLite} from "@codemirror/lang-sql";
function create(parent,o){
  const run=()=>{if(o.onRun)o.onRun();return true;};
  const view=new EditorView({parent,state:EditorState.create({doc:o.doc||"",extensions:[
    lineNumbers(),history(),drawSelection(),bracketMatching(),highlightActiveLine(),indentUnit.of("    "),EditorState.tabSize.of(4),
    syntaxHighlighting(classHighlighter),EditorView.lineWrapping,
    o.lang==="sql"?sql({dialect:SQLite}):python(),
    keymap.of([{key:"Mod-Enter",run},indentWithTab,...defaultKeymap,...historyKeymap]),
    EditorView.contentAttributes.of({autocapitalize:"off",autocorrect:"off",spellcheck:"false","aria-label":"Code editor",autocomplete:"off"}),
    EditorView.updateListener.of(u=>{if(u.docChanged&&o.onChange)o.onChange();})
  ]})});
  return {get:()=>view.state.doc.toString(),set:t=>{view.dispatch({changes:{from:0,to:view.state.doc.length,insert:t}});},
    insert:t=>{view.dispatch(view.state.replaceSelection(t));view.focus();},focus:()=>view.focus(),destroy:()=>view.destroy(),view};
}
window.ShipEditor={create};
