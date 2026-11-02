import { HELP_LINKS, HELP_NOTE } from './helpLovedOne';
export function HelpLovedOne() {
  return <div className="helpLovedOne"><h3>Help your loved one</h3><p>{HELP_NOTE}</p>
    <ul>{HELP_LINKS.map(([t, u]) => <li key={u}><a href={u} target="_blank" rel="noreferrer">{t} ›</a></li>)}</ul></div>;
}
