use serde_json::Value;
use std::fs::read_to_string;
use std::path::Path;
use std::io::{Write};

fn main() {
    let commands: Vec<&str> = vec![
        "install",
        "uninstall",
        "update",
        "bundle",
        "search",
        "new",
        "config",
        "sign",
        "show",
        "find",
        "list",
    ];

    // Set of flags that can be used with `electric install`
    let install_flags = vec![
        "--verbose",
        "--debug",
        "--no-progress",
        "--no-color",
        "--log-output",
        "--install-dir",
        "--virus-check",
        "--yes",
        "--silent",
        "--vscode",
        "--python",
        "--node",
        "--sync",
        "--reduce",
        "--rate-limit",
        "--portable",
        "--manifest"
    ];

    let uninstall_flags = vec![
        "--verbose",
        "--debug",
        "--no-color",
        "--log-output",
        "--yes",
        "--silent",
        "--vscode",
        "--python",
        "--node",
        "--no-cache",
        "--portable",
        "--manifest"
    ];

    let list_flags = vec!["--installed", "--versions"];

    // ["C:\\Users\\xtrem\\Desktop\\Electric\\electric\\src\\rust\\completer\\target\\release\\completer.exe", "--word=in", "--commandline", "electric in", "--position", "11"]
    let args: Vec<String> = std::env::args().collect();
    let typed = &args[3];

    let parse: Vec<&str> = typed.split(" ").collect();

    if parse.len() == 1 {
        // Command: electric

        for command in commands.iter() {
            println!("{}", command);
        }
    } else if parse.len() == 2 {
        // Command: electric install | Command: electric in

        let command = &parse[1];

        if commands.contains(command) {
            // Complete Flags
            for flag in install_flags.iter() {
                println!("{}", flag);
            }
        } else {
            // Complete Command
            for cmd in commands.iter() {
                if cmd.contains(command) {
                    println!("{}", &cmd);
                }
            }
        }
    } else if parse.len() >= 3 {
        // Command: electric install sublime-text | Command: electric install | Command: electric install --verbose
        // Autocomplete Flags
        let command = parse[1].trim();

        match command {
            "install" => {
                let word = &args[1].replace("--word=", "");

                if word.starts_with("--") || word == "" {
                    if word.replace("--", "") == "" {
                        // Complete All Flags
                        for flag in install_flags.iter() {
                            println!("{}", flag);
                        }
                    } else {
                        // Provide Flag-Specific Completion
                        for flag in install_flags.iter() {
                            if flag.contains(word) {
                                println!("{}", flag);
                            }
                        }
                    }
                } else {
                    // Read Json And Complete Packages
                    let appdata = std::env::var("APPDATA").unwrap();
                    let loc = format!(r"{}\electric\packages.json", appdata);
                    let path = Path::new(loc.as_str());

                    if path.exists() {
                        let data = read_to_string(loc).unwrap();
                        let v: Value = serde_json::from_str(data.as_str()).unwrap();
                        let packages = v["packages"].as_array().unwrap();
                        let current = args[1].replace("--word=", "");

                        for package in packages.iter() {
                            let pkg = package.as_str().unwrap().to_string();

                            if pkg.contains(&current) {
                                println!("{}", pkg);
                            }
                        }
                    } else {
                        // Setup / Download packages.json
                        download_file("https://raw.githubusercontent.com/electric-package-manager/electric-packages/master/package-list.json");
                    }
                }
            }
            "uninstall" => {
                let word = &args[1].replace("--word=", "");

                if word.starts_with("--") || word == "" {
                    if word.replace("--", "") == "" {
                        // Complete All Flags
                        for flag in uninstall_flags.iter() {
                            println!("{}", flag);
                        }
                    } else {
                        // Provide Flag-Specific Completion
                        for flag in uninstall_flags.iter() {
                            if flag.contains(word) {
                                println!("{}", flag);
                            }
                        }
                    }
                } else {
                    // Read Json And Complete Packages
                    let appdata = std::env::var("APPDATA").unwrap();
                    let loc = format!(r"{}\electric\packages.json", appdata);
                    let path = Path::new(loc.as_str());

                    if path.exists() {
                        let data = read_to_string(loc).unwrap();
                        let v: Value = serde_json::from_str(data.as_str()).unwrap();
                        let packages = v["packages"].as_array().unwrap();
                        let current = args[1].replace("--word=", "");

                        for package in packages.iter() {
                            let pkg = package.as_str().unwrap().to_string();

                            if pkg.contains(&current) {
                                println!("{}", pkg);
                            }
                        }
                    } else {
                        // Setup / Download packages.json
                        download_file("https://raw.githubusercontent.com/electric-package-manager/electric-packages/master/package-list.json");
                    }
                }
            }
            "update" => {
                let word = &args[1].replace("--word=", "");

                if word.starts_with("--") || word == "" {
                    if word.replace("--", "") == "" {
                        // Complete All Flags
                        for flag in install_flags.iter() {
                            println!("{}", flag);
                        }
                    } else {
                        // Provide Flag-Specific Completion
                        for flag in install_flags.iter() {
                            if flag.contains(word) {
                                println!("{}", flag);
                            }
                        }
                    }
                } else {
                    // Read Json And Complete Packages
                    let appdata = std::env::var("APPDATA").unwrap();
                    let loc = format!(r"{}\electric\packages.json", appdata);
                    let path = Path::new(loc.as_str());

                    if path.exists() {
                        let data = read_to_string(loc).unwrap();
                        let v: Value = serde_json::from_str(data.as_str()).unwrap();
                        let packages = v["packages"].as_array().unwrap();
                        let current = args[1].replace("--word=", "");

                        for package in packages.iter() {
                            let pkg = package.as_str().unwrap().to_string();

                            if pkg.contains(&current) {
                                println!("{}", pkg);
                            }
                        }
                    } else {
                        // Setup / Download packages.json
                        download_file("https://raw.githubusercontent.com/electric-package-manager/electric-packages/master/package-list.json");
                    }
                }
            }
            "bundle" => {
                let word = &args[1].replace("--word=", "");

                if word.starts_with("--") || word == "" {
                    if word.replace("--", "") == "" {
                        // Complete All Flags
                        for flag in install_flags.iter() {
                            println!("{}", flag);
                        }
                    } else {
                        // Provide Flag-Specific Completion
                        for flag in install_flags.iter() {
                            if flag.contains(word) {
                                println!("{}", flag);
                            }
                        }
                    }
                } else {
                    // Read Json And Complete Packages
                    let appdata = std::env::var("APPDATA").unwrap();
                    let loc = format!(r"{}\electric\packages.json", appdata);
                    let path = Path::new(loc.as_str());

                    if path.exists() {
                        let data = read_to_string(loc).unwrap();
                        let v: Value = serde_json::from_str(data.as_str()).unwrap();
                        let packages = v["packages"].as_array().unwrap();
                        let current = args[1].replace("--word=", "");

                        for package in packages.iter() {
                            let pkg = package.as_str().unwrap().to_string();

                            if pkg.contains(&current) {
                                println!("{}", pkg);
                            }
                        }
                    } else {
                        // Setup / Download packages.json
                        download_file("https://raw.githubusercontent.com/electric-package-manager/electric-packages/master/package-list.json");
                    }
                }
            }
            "list" => {
                let word = &args[1].replace("--word=", "");

                if word.starts_with("--") || word == "" {
                    if word.replace("--", "") == "" {
                        // Complete All Flags
                        for flag in list_flags.iter() {
                            println!("{}", flag);
                        }
                    } else {
                        // Provide Flag-Specific Completion
                        for flag in list_flags.iter() {
                            if flag.contains(word) {
                                println!("{}", flag);
                            }
                        }
                    }
                }
            }
            _ => {}
        }
    }
}

fn download_file(url: &str) {
    let mut response: String = String::new();
    
    match minreq::get(url).send() {
        Ok(text) => {
            let res = text.as_str().unwrap();
            if res != "404: Not Found" {
                response = res.to_string();            
            }
        },
        Err(error) => {}
    }

    let loc = format!(r"{}\electric\packages.json", std::env::var("APPDATA").unwrap());
    let mut file = std::fs::File::create(loc).unwrap();
    file.write_all(response.as_bytes()).unwrap();
}