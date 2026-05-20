let services = [
    {
        "title": "Archer",
        "text_box_content_path": "archer",
        "preview_path": "archer",
        "enabled_path": "archer",
        "children": [
            {
                "title": "Boltslinger",
                "text_box_content_path": "archer/boltslinger",
                "preview_path": null,
                "enabled_path": "archer",
                "children": [],
                "issues": [
                    "Guardian Angels: Tracking to be fixed by Wynntils"
                ]
            },
            {
                "title": "Trapper",
                "text_box_content_path": "archer/trapper",
                "preview_path": null,
                "enabled_path": "archer",
                "children": [],
                "issues": [
                    "Basaltic Trap: Tracking currently impossible"
                ]
            },
            {
                "title": "Sharpshooter",
                "text_box_content_path": "archer/sharpshooter",
                "preview_path": null,
                "enabled_path": "archer",
                "children": [],
                "issues": [
                    "Warding Wisps: Tracking currently impossible"
                ]
            }
        ],
        "issues": [
            "Arrow Shield: Tracking to be fixed by Wynntils"
        ]
    },
    {
        "title": "Assassin",
        "text_box_content_path": "assassin",
        "preview_path": "assassin",
        "enabled_path": "assassin",
        "children": [
            {
                "title": "Shadestepper",
                "text_box_content_path": "assassin/shadestepper",
                "preview_path": null,
                "enabled_path": "assassin",
                "children": [],
                "issues": [
                    "Vanish: If the user doesn't have Shadow Travel, it might flash as being ready briefly after expiring"
                ]
            },
            {
                "title": "Trickster",
                "text_box_content_path": "assassin/trickster",
                "preview_path": null,
                "enabled_path": "assassin",
                "children": [],
                "issues": [
                    "Confused / Contaminated / Enkindled / Drained / Hypoxia: Trickster has so many abilities and debuffs that I couldn't figure out a way to fit them all in. These will be added later when I figure that out",
                    "Hoodwink: Tracking currently impossible"
                ]
            },
            {
                "title": "Acrobat",
                "text_box_content_path": "assassin/acrobat",
                "preview_path": null,
                "enabled_path": "assassin",
                "children": [],
                "issues": [
                    "Shurikens: Tracking currently impossible",
                    "Judraijm (Unstable Debuff): Tracking to be added to Wynntils"
                ]
            }
        ],
        "issues": []
    },
    {
        "title": "Mage",
        "text_box_content_path": "mage",
        "preview_path": "mage",
        "enabled_path": "mage",
        "children": [
            {
                "title": "Light Bender",
                "text_box_content_path": "mage/light_bender",
                "preview_path": null,
                "enabled_path": "mage",
                "children": [],
                "issues": [
                    "Lightweaver: Tracking currently impossible"
                ]
            },
            {
                "title": "Riftwalker",
                "text_box_content_path": "mage/riftwalker",
                "preview_path": null,
                "enabled_path": "mage",
                "children": [],
                "issues": []
            },
            {
                "title": "Arcanist",
                "text_box_content_path": "mage/arcanist",
                "preview_path": null,
                "enabled_path": "mage",
                "children": [],
                "issues": []
            }
        ],
        "issues": []
    },
    {
        "title": "Shaman",
        "text_box_content_path": "shaman",
        "preview_path": "shaman",
        "enabled_path": "shaman",
        "children": [
            {
                "title": "Summoner",
                "text_box_content_path": "shaman/summoner",
                "preview_path": null,
                "enabled_path": "shaman",
                "children": [],
                "issues": []
            },
            {
                "title": "Ritualist",
                "text_box_content_path": "shaman/ritualist",
                "preview_path": null,
                "enabled_path": "shaman",
                "children": [],
                "issues": []
            },
            {
                "title": "Acolyte",
                "text_box_content_path": "shaman/acolyte",
                "preview_path": null,
                "enabled_path": "shaman",
                "children": [],
                "issues": [
                    "Blood Sorrow: You can kinda simulate tracking this but its not very consistent",
                    "Eldritch Call: Currently untrackable"
                ]
            }
        ],
        "issues": []
    },
    {
        "title": "Warrior",
        "text_box_content_path": "warrior",
        "preview_path": "warrior",
        "enabled_path": "warrior",
        "children": [
            {
                "title": "Fallen",
                "text_box_content_path": "warrior/fallen",
                "preview_path": null,
                "enabled_path": "warrior",
                "children": [],
                "issues": []
            },
            {
                "title": "Battlemonk",
                "text_box_content_path": "warrior/battlemonk",
                "preview_path": null,
                "enabled_path": "warrior",
                "children": [],
                "issues": []
            },
            {
                "title": "Paladin",
                "text_box_content_path": "warrior/paladin",
                "preview_path": null,
                "enabled_path": "warrior",
                "children": [],
                "issues": [
                    "Mantle of the Bovemist: Charge count tracking to be fixed by Wynntils",
                    "Mantle of the Bovemist looks weird why did you do that: I'm expecting Wynntils to fix mantle tracking soonish? hopefully? so that is where mantles will go. It'll make more sense once that happens"
                ]
            }
        ],
        "issues": []
    }
]

async function copy_template_text(file_path) {
    const response = await fetch(file_path);
    
    if (!response.ok) {
        throw new Error(`File not found: ${response.status}`);
    }
    
    const text = await response.text();

    await navigator.clipboard.writeText(text);
}

function get_issue_doms(service) {
    let output = [];
    for (const issue of service["issues"]) {
        let new_issue_dom = document.createElement("div");
        new_issue_dom.textContent = `(!) ${issue}`;
        output.push(new_issue_dom);
    }
    for (const child of service["children"]) {
        output.push(...get_issue_doms(child));
    }
    return output
}

function create_service_dom(service) {
    let service_dom = document.createElement("div");
    service_dom.classList.add("service");

    let issues_dom = document.createElement("div");
    issues_dom.classList.add("issues");

    let subservices_dom = document.createElement("div");
    subservices_dom.classList.add("service-list");

    let text_box_content_dom = document.createElement("button");
    text_box_content_dom.classList.add("button");
    text_box_content_dom.innerHTML = "Text Box<br>Content";
    text_box_content_dom.addEventListener("click", async () => {
        await copy_template_text(`generated/build/sources/${service["text_box_content_path"]}.infobox`);
        text_box_content_dom.innerHTML = "Copied!";
        setTimeout(() => {
            text_box_content_dom.innerHTML = "Text Box<br>Content";
        }, 4000);
    });
    service_dom.appendChild(text_box_content_dom);

    let enabled_template_dom = document.createElement("button");
    enabled_template_dom.classList.add("button");
    enabled_template_dom.innerHTML = "Enabled<br>Template";
    enabled_template_dom.addEventListener("click", async () => {
        await copy_template_text(`enabled/${service["enabled_path"]}.enabledtemplate`);
        enabled_template_dom.innerHTML = "Copied!";
        setTimeout(() => {
            enabled_template_dom.innerHTML = "Enabled<br>Template";
        }, 4000);
    });
    service_dom.appendChild(enabled_template_dom);

    // expand_dom = document.createElement("button");
    // expand_dom.classList.add("button");
    // expand_dom.innerHTML = "Expand<br>Items";
    // service_dom.appendChild(expand_dom);

    let expand_dom = document.createElement("button");
    expand_dom.classList.add("button", "icon");
    if (service["children"].length == 0) {
        expand_dom.disabled = true;
    } else {
        expand_dom.addEventListener("click", () => {
            if (subservices_dom.children.length > 0) {
                subservices_dom.replaceChildren();
            } else {
                for (subservice of service["children"]) {
                    for (const dom_item of create_service_dom(subservice)) {
                        subservices_dom.appendChild(dom_item);
                    }
                }
            }
        });
    }
    expand_dom.innerHTML = "¦";
    service_dom.appendChild(expand_dom);

    let title_dom = document.createElement("div");
    title_dom.classList.add("title");
    title_dom.innerHTML = service.title;
    service_dom.appendChild(title_dom);

    // edit_dom = document.createElement("button");
    // edit_dom.classList.add("button", "icon");
    // edit_dom.innerHTML = "§";
    // service_dom.appendChild(edit_dom);

    let known_issues_dom = document.createElement("button");
    known_issues_dom.classList.add("button");
    if (get_issue_doms(service).length == 0) {
        known_issues_dom.disabled = true;
    } else {
        known_issues_dom.addEventListener("click", () => {
            if (issues_dom.children.length > 0) {
                issues_dom.replaceChildren();
            } else {
                let issue_doms = get_issue_doms(service);
                for (const issue_dom of issue_doms) {
                    issues_dom.appendChild(issue_dom);
                }
            }
        });
    }
    known_issues_dom.innerHTML = "Known<br>Issues";
    service_dom.appendChild(known_issues_dom);

    let preview_guide_dom = document.createElement("button");
    preview_guide_dom.classList.add("button");
    preview_guide_dom.innerHTML = "Preview<br>/ Guide";
    if (service["preview_path"] === null) {
        preview_guide_dom.disabled = true;
    } else {
        preview_guide_dom.addEventListener("mouseenter", () => {
            let preview_dom = document.createElement("div");
            let preview_image_dom = document.createElement("img");
            preview_image_dom.src = `preview/${service["preview_path"]}.png`;
            preview_image_dom.classList.add("preview");
            preview_dom.style.display = "none";
            preview_dom.classList.add("preview-container");
            preview_image_dom.addEventListener("load", () => {
                preview_dom.style.display = "unset";
                preview_dom.style.left = `${preview_guide_dom.getBoundingClientRect().left + preview_guide_dom.getBoundingClientRect().width - preview_dom.getBoundingClientRect().width}px`;
                preview_dom.style.top = `${preview_guide_dom.getBoundingClientRect().top - preview_dom.getBoundingClientRect().height - 16}px`;
            });
            document.body.children[0].addEventListener("scroll", () => {
                preview_dom.style.left = `${preview_guide_dom.getBoundingClientRect().left + preview_guide_dom.getBoundingClientRect().width - preview_dom.getBoundingClientRect().width}px`;
                preview_dom.style.top = `${preview_guide_dom.getBoundingClientRect().top - preview_dom.getBoundingClientRect().height - 16}px`;
            });
            document.body.children[0].style.filter = "brightness(0.5)";

            let preview_message_dom = document.createElement("div");
            preview_message_dom.classList.add("content", "full-width");
            preview_message_dom.textContent = "Click to view full ability guide";
            preview_dom.appendChild(preview_message_dom);

            preview_dom.appendChild(preview_image_dom);
            document.body.appendChild(preview_dom);
            function remove_preview_callback() {
                document.body.removeChild(preview_dom);
                preview_guide_dom.removeEventListener("mouseleave", remove_preview_callback);
                document.body.children[0].style.filter = "brightness(1.0)";
            }
            preview_guide_dom.addEventListener("mouseleave", remove_preview_callback);
        });
        preview_guide_dom.addEventListener("click", async () => {
            const tab = window.open();
            
            const html_content = `
                <!DOCTYPE html>
                <html>
                <head>
                    <title>${service["title"]} Guide</title>
                    <style>
                        body {
                            background: #222222;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            height: 100vh;
                            margin: 0;
                        }
                        img {
                            width: 90%;
                            image-rendering: -webkit-optimize-contrast;
                            image-rendering: crisp-edges;
                            image-rendering: pixelated;
                            border-radius: 15px;
                            box-shadow: 0px 20px 40px rgba(0,0,0,0.6);
                        }
                    </style>
                    <link rel="icon" type="image/x-icon" href="favicon.ico">
                </head>
                <body>
                    <img src="guide/${service["preview_path"]}.png" alt="Guide">
                </body>
                </html>
            `;
            
            tab.document.write(html_content);
            tab.document.close();
        });
    }
    service_dom.appendChild(preview_guide_dom);

    return [service_dom, issues_dom, subservices_dom];
}

document.addEventListener("DOMContentLoaded", () => {
    let service_list = document.getElementById("service-list");
    for (const service of services) {
        for (const dom_item of create_service_dom(service)) {
            service_list.appendChild(dom_item);
        }
    }
});