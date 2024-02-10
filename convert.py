import re
from typing import Dict, List, Tuple

from utils import (
    DocLink,
    DocPath,
    Settings,
    parse_graph,
    pp,
    raw_dir,
    site_dir,
    write_settings,
)

if __name__ == "__main__":

    Settings.parse_env()
    Settings.sub_file(site_dir / "config.toml")
    Settings.sub_file(site_dir / "content/_index.md")
    Settings.sub_file(site_dir / "templates/macros/footer.html")
    Settings.sub_file(site_dir / "static/js/graph.js")

    nodes: Dict[str, str] = {}
    edges: List[Tuple[str, str]] = []
    section_count = 0

    all_paths = list(sorted(raw_dir.glob("**/*")))

    for path in [raw_dir, *all_paths]:
        doc_path = DocPath(path)
        if doc_path.is_file:
            if doc_path.is_md:
                # Page
                nodes[doc_path.abs_url] = doc_path.page_title
                content = doc_path.content
                parsed_lines: List[str] = []
                for line in content:
                    parsed_line, linked = DocLink.parse(line, doc_path)

                    # Fix LaTEX new lines
                    parsed_line = re.sub(r"\\\\\s*$", r"\\\\\\\\", parsed_line)

                    parsed_lines.append(parsed_line)

                    edges.extend([doc_path.edge(rel_path) for rel_path in linked])

                content = [
                    "---",
                    f'title: "{doc_path.page_title}"',
                    f"date: {doc_path.modified}",
                    f"updated: {doc_path.modified}",
                    "template: docs/page.html",
                    "---",
                    # To add last line-break
                    "",
                ]
                doc_path.write(["\n".join(content), *parsed_lines])
                print(f"Found page: {doc_path.new_rel_path}")
            else:
                # Resource
                doc_path.copy()
                print(f"Found resource: {doc_path.new_rel_path}")
        else:
            """Section"""
            # Frontmatter
            # TODO: sort_by depends on settings
            content = [
                "---",
                f'title: "{doc_path.section_title}"',
                "template: docs/section.html",
                f"sort_by: {Settings.options['SORT_BY']}",
                f"weight: {section_count}",
                "extra:",
                f"    sidebar: {doc_path.section_sidebar}",
                "---",
                # To add last line-break
                "",
            ]
            section_count += 1
            doc_path.write_to("_index.md", "\n".join(content))
            print(f"Found section: {doc_path.new_rel_path}")


    latest_count = 0;
    index_parsed_lines: List[str] = []
    all_paths.reverse()
    next_entry_title = "/"
    for path in all_paths:

        print (str(path))
        doc_path = DocPath(path)
            # case when there are 5 or less  entries are not hanled
        if (latest_count == 6):
            next_entry_title = doc_path.page_title
            break;
    

        if doc_path.is_file & doc_path.is_md:
            content = doc_path.content

            # add title
            index_parsed_lines.append("## " + doc_path.page_title + '\n')
            for line in content:
                parsed_line, linked = DocLink.parse(line, doc_path)

                # Fix LaTEX new lines
                parsed_line = re.sub(r"\\\\\s*$", r"\\\\\\\\", parsed_line)

                index_parsed_lines.append(parsed_line)   
            latest_count += 1 




    content = [
                    "---",
                    f"title: {Settings.options['LANDING_TITLE']}",
                    f"sort_by: {Settings.options['SORT_BY']}",

                    f"extra: ",
                    f"  next_entry_url: \"/docs/" + next_entry_title + "\"",
                    "---",
                    # To add last line-break
                    "",
                ]
    index = site_dir / "content/_index.md"
    index.write_text("".join(["\n".join(content), *index_parsed_lines]))


    pp(nodes)
    pp(edges)
    parse_graph(nodes, edges)
    write_settings()
