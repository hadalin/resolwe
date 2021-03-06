from resolwe import process
from resolwe.process import (
    Cmd,
    DataField,
    DirField,
    FileField,
    FloatField,
    GroupField,
    IntegerField,
    JsonField,
    ListField,
    Persistence,
    Process,
    SchedulingClass,
    StringField,
    UrlField,
)


class EntityProcess(Process):
    slug = "entity-process"
    name = "Entity process"
    data_name = "Data with entity"
    version = "1.0.0"
    process_type = "data:entity"
    entity = {
        "type": "sample",
    }

    class Output:
        list_string = ListField(StringField(), label="My list")
        optional = StringField("Optional output", required=False)

    def run(self, inputs, outputs):
        outputs.list_string = ["foo", "bar"]


class PythonProcess(Process):
    """This is a process description."""

    slug = "test-python-process"
    name = "Test Python Process"
    version = "0.1.2"
    process_type = "data:python"
    category = "analyses"
    scheduling_class = SchedulingClass.BATCH
    persistence = Persistence.CACHED
    data_name = "Foo: {{input_data | name}}"
    entity = {
        "type": "sample",
        "descriptor_schema": "sample",
        "input": "input_data",
    }
    requirements = {
        "expression-engine": "jinja",
        "executor": {"docker": {"image": "resolwe/base:ubuntu-18.04",}},
    }

    class Input:
        """Input fields."""

        my_field = StringField(label="My field")
        my_list = ListField(StringField(), label="My list")
        input_data = DataField("test:save", label="My input data")
        input_entity_data = DataField("entity", label="My entity data")
        bar = DataField(data_type="test:save", label="My bar")
        url = UrlField(UrlField.DOWNLOAD, label="My URL")
        integer = IntegerField(label="My integer")
        my_float = FloatField(label="My float")
        my_json = JsonField(label="Blah blah")
        my_optional = StringField(
            label="Optional", required=False, default="default value"
        )
        my_optional_no_default = StringField(
            label="Optional no default", required=False
        )

        class MyGroup:
            foo = IntegerField(label="Foo")
            bar = StringField(label="Bar")
            group_optional_no_default = StringField(
                label="Group optional no default", required=False
            )

        my_group = GroupField(MyGroup, label="My group")

    class Output:
        string_output = StringField(label="My string output")
        list_string_output = ListField(StringField(), label="My list string output")
        file_output = FileField(label="My output")
        list_file_output = ListField(FileField(), label="My list output")
        dir_output = DirField(label="My output")
        input_data_name = StringField(label="Input data name")
        input_entity_name = StringField(label="Input entity name")
        docker_image = StringField(label="Docker image")

    def run(self, inputs, outputs):
        print("All inputs are:", inputs)
        print("Input data:", inputs.input_data)
        print("Input data ID:", inputs.input_data.id)
        print("Input data file output:", inputs.input_data.saved_file.path)
        print("Input data type:", inputs.input_data.type)
        print("Input data descriptor:", inputs.input_data.descriptor)
        print("Group bar:", inputs.my_group.bar)
        print("Group foo:", inputs.my_group.foo)
        print("Entity name of the input:", inputs.input_entity_data.entity_name)
        print("Docker image:", self.requirements.executor.docker.image)

        if inputs.my_optional:
            print("My optional:", inputs.my_optional)

        if inputs.my_optional_no_default:
            raise AttributeError("inputs.my_optional_no_default should not exist.")

        if inputs.my_group.group_optional_no_default:
            raise AttributeError(
                "inputs.my_group.group_optional_no_default should not exist."
            )

        if inputs.input_entity_data.optional:
            raise AttributeError("inputs.list_string_output.optional should not exist.")

        try:
            inputs.invalid_input
        except AttributeError as err:
            if "Inputs have no field invalid_input" in str(err):
                pass

        try:
            inputs.input_entity_data.invalid_field
        except AttributeError as err:
            if "DataField has no member invalid_field" in str(err):
                pass

        bar = Cmd["ls"]["-l", "-a", "/"] | Cmd["grep"]["python"]
        print("hello world:\n", bar())

        Cmd["mkdir"]["test"]()
        (Cmd["echo"]['"Some content"'] > "test/testfile.txt")()
        (Cmd["echo"]['"Some more content"'] > "testfile2.txt")()

        outputs.file_output = "test/testfile.txt"
        outputs.list_file_output = ["test/testfile.txt", "testfile2.txt"]
        outputs.dir_output = "test/"
        outputs.input_data_name = inputs.input_data.name
        outputs.input_entity_name = inputs.input_entity_data.entity_name
        outputs.docker_image = self.requirements.executor.docker.image
        outputs.string_output = "OK"
        outputs.list_string_output = ["foo", "bar"]


class PythonProcessGroup(Process):
    """Process with Group fields."""

    slug = "test-python-process-group-field"
    name = "Test Python Process for GroupField"
    version = "0.1.2"
    process_type = "data:python:group"

    class Input:
        """Input fields."""

        class MyGroup:
            foo = IntegerField(label="Foo", required=False, default=42)
            bar = StringField(label="Bar", required=False)

        class MyGroup2:
            foo = IntegerField(label="Foo", required=False)

        my_group = GroupField(MyGroup, label="My group")
        my_group2 = GroupField(
            MyGroup2, label="My group2 that has all elements without defaults."
        )

    class Output:
        """Output fields."""

        out_foo = IntegerField(label="Foo.", required=False)
        out_bar = StringField(label="Bar.", required=False)
        out_foo2 = IntegerField(label="Foo2.", required=False)

    def run(self, inputs, outputs):
        if inputs.my_group.foo:
            outputs.out_foo = inputs.my_group.foo
        if inputs.my_group.bar:
            outputs.out_bar = inputs.my_group.bar
        if inputs.my_group2.foo:
            outputs.out_foo2 = inputs.my_group2.foo


class PythonProcess2(process.Process):
    """Inherit from 'module.Class'."""

    slug = "test-python-process-2"
    name = "Test Python Process 2"
    version = "0.0.1"
    process_type = "data:python"

    def run(self, inputs, outputs):
        pass


class ErrorProcess(Process):
    slug = "test-python-process-error"
    name = "Test Python Process Error"
    version = "0.0.1"
    process_type = "data:python:error"

    def run(self, inputs, outputs):
        raise ValueError("Value error in ErrorProcess")


class AnnotateProcess(Process):
    slug = "test-python-process-annotate-entity"
    name = "Test Python Process Annotate Entity"
    version = "0.0.1"
    process_type = "data:python:annotate"
    entity = {
        "type": "sample",
    }

    def run(self, inputs, outputs):
        annotations = {
            "general.description": "desc",
            "general.species": "Valid"
        }
        self.update_entity_descriptor(annotations)


class FileProcess(Process):
    slug = "test-python-process-file"
    name = "Test Python Process File"
    version = "0.0.1"
    process_type = "data:python:file"

    class Input:
        """Input fields."""

        src = FileField(label="Input file")

    class Output:
        """Input fields."""

        dst = FileField(label="Output file")

    def run(self, inputs, outputs):
        file_name = inputs.src.import_file()
        outputs.dst = file_name


class RequirementsProcess(Process):
    slug = "test-python-process-requirements"
    name = "Test Python Process Requirements"
    version = "0.0.1"
    process_type = "data:python:requirements"
    requirements = {
        "resources": {"cores": 2, "memory": 4096,},
    }

    class Output:
        """Input fields."""

        cores = IntegerField(label="Cores")
        memory = IntegerField(label="Memory")

    def run(self, inputs, outputs):
        outputs.cores = self.requirements["resources"]["cores"]
        outputs.memory = self.requirements["resources"]["memory"]

        print("Cores:", outputs.cores)
        print("Memory:", outputs.memory)


class ProcessWithWorkflowInput(Process):
    slug = "process-with-workflow-input"
    name = "Process with workflow input"
    version = "1.0.0"
    process_type = "data:test"

    class Input:
        """Input fields."""

        data = DataField(data_type="", label="Data.")

    def run(self, inputs, outputs):
        pass

class ProcessWithChoicesInput(Process):
    slug = "process-with-choices-input"
    name = "Process with choices input"
    version = "1.0.0"
    process_type = "data:test"

    class Input:
        """Input fields."""
        string_input = StringField(
            label="Input field",
            allow_custom_choice=True,
            choices=[
                ("foo", "foo"),
                ("bar", "bar"),
            ]
        )

    class Output:
        """Output fields."""
        string_output = StringField(label="Output field")

    def run(self, inputs, outputs):
        outputs.string_output = inputs.string_input
