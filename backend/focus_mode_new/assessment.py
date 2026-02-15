import statistics

QUESTION_BANK = {
    "Physics": [
        {
            "question": "What is motion?",
            "options": {
                1: "Motion means something is moving.",
                2: "Motion is when an object changes its place.",
                3: "Motion is the change in position of an object over time.",
                4: "Motion is the variation of an object’s position with respect to time and reference frame."
            }
        },
        {
            "question": "What is force?",
            "options": {
                1: "Force is a push or pull.",
                2: "Force is a push or pull that changes motion.",
                3: "Force is an interaction that can change motion or shape.",
                4: "Force is a physical interaction that produces acceleration or deformation."
            }
        },
        {
            "question": "What is energy?",
            "options": {
                1: "Energy is the ability to do work.",
                2: "Energy helps us do work or move things.",
                3: "Energy is the capacity to perform work.",
                4: "Energy is a quantitative property that must be transferred to perform work."
            }
        },
        {
            "question": "What is speed?",
            "options": {
                1: "Speed tells how fast something moves.",
                2: "Speed is how fast an object moves.",
                3: "Speed is the distance travelled per unit time.",
                4: "Speed is a scalar quantity representing rate of change of distance."
            }
        },
        {
            "question": "What is gravity?",
            "options": {
                1: "Gravity pulls things down.",
                2: "Gravity is the force that pulls objects to Earth.",
                3: "Gravity is a force that attracts objects toward each other.",
                4: "Gravity is a universal force of attraction acting between masses."
            }
        }
    ],

    "Chemistry": [
        {
            "question": "What is an atom?",
            "options": {
                1: "An atom is a tiny part of matter.",
                2: "An atom is the smallest part of an element.",
                3: "An atom is the basic unit of matter.",
                4: "An atom is the smallest unit retaining chemical properties of an element."
            }
        },
        {
            "question": "What is a molecule?",
            "options": {
                1: "A molecule is two or more atoms together.",
                2: "A molecule is formed when atoms join.",
                3: "A molecule is a group of atoms bonded together.",
                4: "A molecule is an electrically neutral group of atoms held by chemical bonds."
            }
        },
        {
            "question": "What is a chemical reaction?",
            "options": {
                1: "A reaction is when substances change.",
                2: "A reaction is when substances form something new.",
                3: "A chemical reaction forms new substances.",
                4: "A chemical reaction involves rearrangement of atoms into new compounds."
            }
        },
        {
            "question": "What is matter?",
            "options": {
                1: "Matter is anything around us.",
                2: "Matter is anything that has mass.",
                3: "Matter has mass and takes up space.",
                4: "Matter is anything that has mass and occupies volume."
            }
        },
        {
            "question": "What is an element?",
            "options": {
                1: "An element is a pure substance.",
                2: "An element is made of one type of atom.",
                3: "An element contains only one kind of atom.",
                4: "An element is a substance that cannot be chemically broken down."
            }
        }
    ],

    "Biology": [
        {
            "question": "What is a cell?",
            "options": {
                1: "A cell is a tiny part of a living thing.",
                2: "A cell is the smallest unit of life.",
                3: "A cell is the basic unit of living organisms.",
                4: "A cell is the fundamental structural and functional unit of life."
            }
        },
        {
            "question": "What is photosynthesis?",
            "options": {
                1: "Plants make food using sunlight.",
                2: "Plants use sunlight to make food.",
                3: "Plants convert sunlight into food energy.",
                4: "Plants synthesize glucose using solar energy, CO₂, and water."
            }
        },
        {
            "question": "What is respiration?",
            "options": {
                1: "Respiration helps us breathe.",
                2: "Respiration releases energy from food.",
                3: "Respiration is how cells get energy.",
                4: "Respiration is a metabolic process that releases energy from glucose."
            }
        },
        {
            "question": "What is tissue?",
            "options": {
                1: "A tissue is a group of cells.",
                2: "A tissue is similar cells working together.",
                3: "A tissue is a group of similar cells with a function.",
                4: "A tissue is an organized group of similar cells performing specific functions."
            }
        },
        {
            "question": "What is growth?",
            "options": {
                1: "Growth means getting bigger.",
                2: "Growth is increase in size.",
                3: "Growth is increase in size and number of cells.",
                4: "Growth is a permanent increase in size due to cell division."
            }
        }
    ],

    "SST": [
        {
            "question": "What is democracy?",
            "options": {
                1: "People choose their leaders.",
                2: "People elect their government.",
                3: "Democracy is rule by the people.",
                4: "Democracy is a system of government based on popular participation."
            }
        },
        {
            "question": "What is a constitution?",
            "options": {
                1: "Rules for a country.",
                2: "A set of rules for governance.",
                3: "A constitution defines laws of a country.",
                4: "A constitution is the supreme legal framework of a nation."
            }
        },
        {
            "question": "What is history?",
            "options": {
                1: "Study of the past.",
                2: "Study of past events.",
                3: "History studies human past activities.",
                4: "History is the systematic study of past human events."
            }
        },
        {
            "question": "What is geography?",
            "options": {
                1: "Study of Earth.",
                2: "Study of land and places.",
                3: "Geography studies Earth’s features.",
                4: "Geography studies physical and human features of Earth."
            }
        },
        {
            "question": "What is government?",
            "options": {
                1: "People who rule a country.",
                2: "System that runs a country.",
                3: "Government manages public affairs.",
                4: "Government is an authority that administers a state."
            }
        }
    ]
}


def conduct_language_assessment(subject):
    selected_levels = []

    print("\nSelect the option you understand BEST.\n")

    for q in QUESTION_BANK[subject]:
        print("\n" + q["question"])
        for level in range(1, 5):
            print(f"{level}. {q['options'][level]}")

        choice = int(input("Your choice (1–4): "))
        selected_levels.append(choice)

    return int(statistics.median(selected_levels))
