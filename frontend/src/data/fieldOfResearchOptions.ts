export interface FoRGroup {
    value: string;
    label: string;
}

export interface FoRDivision {
    value: string;
    label: string;
    groups: FoRGroup[];
}

export const fieldOfResearchOptions: FoRDivision[] = [
    // 30 — Agricultural, Veterinary and Food Sciences
    {
        value: '30',
        label: 'Agricultural, Veterinary and Food Sciences',
        groups: [
            { value: '3001', label: 'Agricultural biotechnology' },
            { value: '3002', label: 'Agriculture, land and farm management' },
            { value: '3003', label: 'Animal production' },
            { value: '3004', label: 'Crop and pasture production' },
            { value: '3005', label: 'Fisheries sciences' },
            { value: '3006', label: 'Food sciences' },
            { value: '3007', label: 'Forestry sciences' },
            { value: '3008', label: 'Horticultural production' },
            { value: '3009', label: 'Veterinary sciences' },
            { value: '3099', label: 'Other agricultural, veterinary and food sciences' },
        ],
    },

    // 31 — Biological Sciences
    {
        value: '31',
        label: 'Biological Sciences',
        groups: [
            { value: '3101', label: 'Biochemistry and cell biology' },
            { value: '3102', label: 'Bioinformatics and computational biology' },
            { value: '3103', label: 'Ecology' },
            { value: '3104', label: 'Evolutionary biology' },
            { value: '3105', label: 'Genetics' },
            { value: '3106', label: 'Industrial biotechnology' },
            { value: '3107', label: 'Microbiology' },
            { value: '3108', label: 'Plant biology' },
            { value: '3109', label: 'Zoology' },
            { value: '3199', label: 'Other biological sciences' },
        ],
    },

    // 32 — Biomedical and Clinical Sciences
    { 
        value: '32', 
        label: 'Biomedical and Clinical Sciences',
        groups: [
            { value: '3201', label: 'Cardiovascular medicine and haematology' },
            { value: '3202', label: 'Clinical sciences' },
            { value: '3203', label: 'Dentistry' },
            { value: '3204', label: 'Immunology' },
            { value: '3205', label: 'Medical biochemistry and metabolomics' },
            { value: '3206', label: 'Medical biotechnology' },
            { value: '3207', label: 'Medical microbiology' },
            { value: '3208', label: 'Medical physiology' },
            { value: '3209', label: 'Neurosciences' },
            { value: '3210', label: 'Nutrition and dietetics' },
            { value: '3211', label: 'Oncology and carcinogenesis' },
            { value: '3212', label: 'Ophthalmology and optometry' },
            { value: '3213', label: 'Paediatrics' },
            { value: '3214', label: 'Pharmacology and pharmaceutical sciences' },
            { value: '3215', label: 'Reproductive medicine' },
            { value: '3299', label: 'Other biomedical and clinical sciences' },
        ],
    },

    // 33 — Built Environment and Design
    { 
        value: '33', 
        label: 'Built Environment and Design',
        groups: [
            { value: '3301', label: 'Architecture' },
            { value: '3302', label: 'Building' },
            { value: '3303', label: 'Design' },
            { value: '3304', label: 'Urban and regional planning' },
            { value: '3399', label: 'Other built environment and design' },
        ],
    },

    // 34 — Chemical Sciences
    { 
        value: '34', 
        label: 'Chemical Sciences',
        groups: [
            { value: '3401', label: 'Analytical chemistry' },
            { value: '3402', label: 'Inorganic chemistry' },
            { value: '3403', label: 'Macromolecular and materials chemistry' },
            { value: '3404', label: 'Medicinal and biomolecular chemistry' },
            { value: '3405', label: 'Organic chemistry' },
            { value: '3406', label: 'Physical chemistry' },
            { value: '3407', label: 'Theoretical and computational chemistry' },
            { value: '3499', label: 'Other chemical sciences' },
        ],
    },

    // 35 — Commerce, Management, Tourism and Services
    {
        value: '35',
        label: 'Commerce, Management, Tourism and Services',
        groups: [
            { value: '3501', label: 'Accounting, auditing and accountability' },
            { value: '3502', label: 'Banking, finance and investment' },
            { value: '3503', label: 'Business systems in context' },
            { value: '3504', label: 'Commercial services' },
            { value: '3505', label: 'Human resources and industrial relations' },
            { value: '3506', label: 'Marketing' },
            { value: '3507', label: 'Strategy, management and organisational behaviour' },
            { value: '3508', label: 'Tourism' },
            { value: '3509', label: 'Transportation, logistics and supply chains' },
            { value: '3599', label: 'Other commerce, management, tourism and services' },
        ],
    },

    // 36 — Creative Arts and Writing
    {
        value: '36',
        label: 'Creative Arts and Writing',
        groups: [
            { value: '3601', label: 'Art history, theory and criticism' },
            { value: '3602', label: 'Creative and professional writing' },
            { value: '3603', label: 'Music' },
            { value: '3604', label: 'Performing arts' },
            { value: '3605', label: 'Screen and digital media' },
            { value: '3606', label: 'Visual arts' },
            { value: '3699', label: 'Other creative arts and writing' },
        ],
    },

    // 37 — Earth Sciences
    {
        value: '37',
        label: 'Earth Sciences',
        groups: [
            { value: '3701', label: 'Atmospheric sciences' },
            { value: '3702', label: 'Climate change science' },
            { value: '3703', label: 'Geochemistry' },
            { value: '3704', label: 'Geoinformatics' },
            { value: '3705', label: 'Geology' },
            { value: '3706', label: 'Geophysics' },
            { value: '3707', label: 'Hydrology' },
            { value: '3708', label: 'Oceanography' },
            { value: '3709', label: 'Physical geography and environmental geoscience' },
            { value: '3799', label: 'Other earth sciences' },
        ],
    },

    // 38 — Economics
    {
        value: '38',
        label: 'Economics',
        groups: [
            { value: '3801', label: 'Applied economics' },
            { value: '3802', label: 'Econometrics' },
            { value: '3803', label: 'Economic theory' },
            { value: '3899', label: 'Other economics' },
        ],
    },

    // 39 — Education
    {
        value: '39',
        label: 'Education',
        groups: [
            { value: '3901', label: 'Curriculum and pedagogy' },
            { value: '3902', label: 'Education policy, sociology and philosophy' },
            { value: '3903', label: 'Education systems' },
            { value: '3904', label: 'Specialist studies in education' },
            { value: '3999', label: 'Other education' },
        ],
    },

    // 40 — Engineering
    {
        value: '40',
        label: 'Engineering',
        groups: [
            { value: '4001', label: 'Aerospace engineering' },
            { value: '4002', label: 'Automotive engineering' },
            { value: '4003', label: 'Biomedical engineering' },
            { value: '4004', label: 'Chemical engineering' },
            { value: '4005', label: 'Civil engineering' },
            { value: '4006', label: 'Communications engineering' },
            { value: '4007', label: 'Control engineering, mechatronics and robotics' },
            { value: '4008', label: 'Electrical engineering' },
            { value: '4009', label: 'Electronics, sensors and digital hardware' },
            { value: '4010', label: 'Engineering practice and education' },
            { value: '4011', label: 'Environmental engineering' },
            { value: '4012', label: 'Fluid mechanics and thermal engineering' },
            { value: '4013', label: 'Geomatic engineering' },
            { value: '4014', label: 'Manufacturing engineering' },
            { value: '4015', label: 'Maritime engineering' },
            { value: '4016', label: 'Materials engineering' },
            { value: '4017', label: 'Mechanical engineering' },
            { value: '4018', label: 'Nanotechnology' },
            { value: '4019', label: 'Resources engineering and extractive metallurgy' },
            { value: '4099', label: 'Other engineering' },
        ],
    },

    // 41 — Environmental Sciences
    {
        value: '41',
        label: 'Environmental Sciences',
        groups: [
            { value: '4101', label: 'Climate change impacts and adaptation' },
            { value: '4102', label: 'Ecological applications' },
            { value: '4103', label: 'Environmental biotechnology' },
            { value: '4104', label: 'Environmental management' },
            { value: '4105', label: 'Pollution and contamination' },
            { value: '4106', label: 'Soil sciences' },
            { value: '4199', label: 'Other environmental sciences' },
        ],
    },

    // 42 — Health Sciences
    {
        value: '42',
        label: 'Health Sciences',
        groups: [
            { value: '4201', label: 'Allied health and rehabilitation science' },
            { value: '4202', label: 'Epidemiology' },
            { value: '4203', label: 'Health services and systems' },
            { value: '4204', label: 'Midwifery' },
            { value: '4205', label: 'Nursing' },
            { value: '4206', label: 'Public health' },
            { value: '4207', label: 'Sports science and exercise' },
            { value: '4208', label: 'Traditional, complementary and integrative medicine' },
            { value: '4299', label: 'Other health sciences' },
        ],
    },

    // 43 — History, Heritage and Archaeology
    {
        value: '43',
        label: 'History, Heritage and Archaeology',
        groups: [
            { value: '4301', label: 'Archaeology' },
            { value: '4302', label: 'Heritage, archive and museum studies' },
            { value: '4303', label: 'Historical studies' },
            { value: '4399', label: 'Other history, heritage and archaeology' },
        ],
    },

    // 44 — Human Society
    {
        value: '44',
        label: 'Human Society',
        groups: [
            { value: '4401', label: 'Anthropology' },
            { value: '4402', label: 'Criminology' },
            { value: '4403', label: 'Demography' },
            { value: '4404', label: 'Development studies' },
            { value: '4405', label: 'Gender studies' },
            { value: '4406', label: 'Human geography' },
            { value: '4407', label: 'Policy and administration' },
            { value: '4408', label: 'Political science' },
            { value: '4409', label: 'Social work' },
            { value: '4410', label: 'Sociology' },
            { value: '4499', label: 'Other human society' },
        ],
    },

    // 45 — Indigenous Studies
    {
        value: '45',
        label: 'Indigenous Studies',
        groups: [
            { value: '4501', label: 'Aboriginal and Torres Strait Islander culture, language and history' },
            { value: '4502', label: 'Aboriginal and Torres Strait Islander education' },
            { value: '4503', label: 'Aboriginal and Torres Strait Islander environmental knowledges and management' },
            { value: '4504', label: 'Aboriginal and Torres Strait Islander health and wellbeing' },
            { value: '4505', label: 'Aboriginal and Torres Strait Islander peoples, society and community' },
            { value: '4506', label: 'Aboriginal and Torres Strait Islander sciences' },
            { value: '4507', label: 'Te ahurea, reo me te hītori o te Māori (Māori culture, language and history)' },
            { value: '4508', label: 'Mātauranga Māori (Māori education)' },
            { value: '4509', label: 'Ngā mātauranga taiao o te Māori (Māori environmental knowledges)' },
            { value: '4510', label: 'Te hauora me te oranga o te Māori (Māori health and wellbeing)' },
            { value: '4511', label: 'Ngā tāngata, te porihanga me ngā hapori o te Māori (Māori peoples, society and community)' },
            { value: '4512', label: 'Ngā pūtaiao Māori (Māori sciences)' },
            { value: '4513', label: 'Pacific Peoples culture, language and history' },
            { value: '4514', label: 'Pacific Peoples education' },
            { value: '4515', label: 'Pacific Peoples environmental knowledges' },
            { value: '4516', label: 'Pacific Peoples health and wellbeing' },
            { value: '4517', label: 'Pacific Peoples sciences' },
            { value: '4518', label: 'Pacific Peoples society and community' },
            { value: '4519', label: 'Other Indigenous data, methodologies and global Indigenous studies' },
            { value: '4599', label: 'Other Indigenous studies' },
        ],
    },

    // 46 — Information and Computing Sciences
    {
        value: '46',
        label: 'Information and Computing Sciences',
        groups: [
            { value: '4601', label: 'Applied computing' },
            { value: '4602', label: 'Artificial intelligence' },
            { value: '4603', label: 'Computer vision and multimedia computation' },
            { value: '4604', label: 'Cybersecurity and privacy' },
            { value: '4605', label: 'Data management and data science' },
            { value: '4606', label: 'Distributed computing and systems software' },
            { value: '4607', label: 'Graphics, augmented reality and games' },
            { value: '4608', label: 'Human-centred computing' },
            { value: '4609', label: 'Information systems' },
            { value: '4610', label: 'Library and information studies' },
            { value: '4611', label: 'Machine learning' },
            { value: '4612', label: 'Software engineering' },
            { value: '4613', label: 'Theory of computation' },
            { value: '4699', label: 'Other information and computing sciences' },
        ],
    },

    // 47 — Language, Communication and Culture
    {
        value: '47',
        label: 'Language, Communication and Culture',
        groups: [
            { value: '4701', label: 'Communication and media studies' },
            { value: '4702', label: 'Cultural studies' },
            { value: '4703', label: 'Language studies' },
            { value: '4704', label: 'Linguistics' },
            { value: '4705', label: 'Literary studies' },
            { value: '4799', label: 'Other language, communication and culture' },
        ],
    },

    // 48 — Law and Legal Studies
    {
        value: '48',
        label: 'Law and Legal Studies',
        groups: [
            { value: '4801', label: 'Commercial law' },
            { value: '4802', label: 'Environmental and resources law' },
            { value: '4803', label: 'International and comparative law' },
            { value: '4804', label: 'Law in context' },
            { value: '4805', label: 'Legal systems' },
            { value: '4806', label: 'Private law and civil obligations' },
            { value: '4807', label: 'Public law' },
            { value: '4899', label: 'Other law and legal studies' },
        ],
    },

    // 49 — Mathematical Sciences
    {
        value: '49',
        label: 'Mathematical Sciences',
        groups: [
            { value: '4901', label: 'Applied mathematics' },
            { value: '4902', label: 'Mathematical physics' },
            { value: '4903', label: 'Numerical and computational mathematics' },
            { value: '4904', label: 'Pure mathematics' },
            { value: '4905', label: 'Statistics' },
            { value: '4999', label: 'Other mathematical sciences' },
        ],
    },

    // 50 — Philosophy and Religious Studies
    {
        value: '50',
        label: 'Philosophy and Religious Studies',
        groups: [
            { value: '5001', label: 'Applied ethics' },
            { value: '5002', label: 'History and philosophy of specific fields' },
            { value: '5003', label: 'Philosophy' },
            { value: '5004', label: 'Religious studies' },
            { value: '5005', label: 'Theology' },
            { value: '5099', label: 'Other philosophy and religious studies' },
        ],
    },

    // 51 — Physical Sciences
    {
        value: '51',
        label: 'Physical Sciences',
        groups: [
            { value: '5101', label: 'Astronomical sciences' },
            { value: '5102', label: 'Atomic, molecular and optical physics' },
            { value: '5103', label: 'Classical physics' },
            { value: '5104', label: 'Condensed matter physics' },
            { value: '5105', label: 'Medical and biological physics' },
            { value: '5106', label: 'Nuclear and plasma physics' },
            { value: '5107', label: 'Particle and high energy physics' },
            { value: '5108', label: 'Quantum physics' },
            { value: '5109', label: 'Space sciences' },
            { value: '5110', label: 'Synchrotrons and accelerators' },
            { value: '5199', label: 'Other physical sciences' },
        ],
    },

    // 52 — Psychology
    {
        value: '52',
        label: 'Psychology',
        groups: [
            { value: '5201', label: 'Applied and developmental psychology' },
            { value: '5202', label: 'Biological psychology' },
            { value: '5203', label: 'Clinical and health psychology' },
            { value: '5204', label: 'Cognitive and computational psychology' },
            { value: '5205', label: 'Social and personality psychology' },
            { value: '5299', label: 'Other psychology' },
        ],
    },
];