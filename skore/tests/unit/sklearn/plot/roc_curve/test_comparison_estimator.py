import matplotlib as mpl
import numpy as np
import pytest
from sklearn.base import clone
from skore import ComparisonReport, EstimatorReport
from skore.sklearn._plot import RocCurveDisplay
from skore.sklearn._plot.utils import sample_mpl_colormap
from skore.utils._testing import check_frame_structure, check_legend_position
from skore.utils._testing import check_roc_curve_display_data as check_display_data


def test_binary_classification(pyplot, binary_classification_data):
    """Check the attributes and default plotting behaviour of the ROC curve plot with
    binary data."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.roc()
    assert isinstance(display, RocCurveDisplay)
    check_display_data(display)

    assert (
        list(display.roc_curve["label"].unique())
        == list(display.roc_auc["label"].unique())
        == [estimator.classes_[1]]
        == [display.pos_label]
    )

    display.plot()
    expected_colors = sample_mpl_colormap(pyplot.cm.tab10, 10)
    for idx, (estimator_name, line) in enumerate(
        zip(report.report_names_, display.lines_, strict=False)
    ):
        assert isinstance(line, mpl.lines.Line2D)
        roc_auc_class = display.roc_auc.query(
            f"label == {display.pos_label} & estimator_name == '{estimator_name}'"
        )["roc_auc"].item()
        assert line.get_label() == (f"{estimator_name} (AUC = {roc_auc_class:0.2f})")
        assert mpl.colors.to_rgba(line.get_color()) == expected_colors[idx]

    assert isinstance(display.chance_level_, mpl.lines.Line2D)
    assert display.chance_level_.get_label() == "Chance level (AUC = 0.5)"
    assert display.chance_level_.get_color() == "k"

    assert isinstance(display.ax_, mpl.axes.Axes)
    legend = display.ax_.get_legend()
    assert legend.get_title().get_text() == "Test set"
    assert len(legend.get_texts()) == 2 + 1

    assert display.ax_.get_xlabel() == "False Positive Rate\n(Positive label: 1)"
    assert display.ax_.get_ylabel() == "True Positive Rate\n(Positive label: 1)"
    assert display.ax_.get_adjustable() == "box"
    assert display.ax_.get_aspect() in ("equal", 1.0)
    assert display.ax_.get_xlim() == display.ax_.get_ylim() == (-0.01, 1.01)
    assert display.ax_.get_title() == "ROC Curve"


def test_multiclass_classification(pyplot, multiclass_classification_data):
    """Check the attributes and default plotting behaviour of the ROC curve plot with
    multiclass data."""
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.roc()

    assert isinstance(display, RocCurveDisplay)
    check_display_data(display)
    class_labels = report.reports_[0].estimator_.classes_
    assert (
        list(display.roc_curve["label"].unique())
        == list(display.roc_auc["label"].unique())
        == list(class_labels)
    )

    display.plot()
    assert isinstance(display.lines_, list)
    assert len(display.lines_) == len(class_labels) * 2
    default_colors = sample_mpl_colormap(pyplot.cm.tab10, 10)
    for idx, (estimator_name, expected_color) in enumerate(
        zip(report.report_names_, default_colors, strict=False)
    ):
        for class_label_idx, class_label in enumerate(class_labels):
            roc_curve_mpl = display.lines_[idx * len(class_labels) + class_label_idx]
            assert isinstance(roc_curve_mpl, mpl.lines.Line2D)
            roc_auc_class = display.roc_auc.query(
                f"label == {class_label} & estimator_name == '{estimator_name}'"
            )["roc_auc"].item()
            assert roc_curve_mpl.get_label() == (
                f"{estimator_name} - {str(class_label).title()} "
                f"(AUC = {roc_auc_class:0.2f})"
            )
            assert roc_curve_mpl.get_color() == expected_color

    assert isinstance(display.chance_level_, mpl.lines.Line2D)
    assert display.chance_level_.get_label() == "Chance level (AUC = 0.5)"
    assert display.chance_level_.get_color() == "k"

    assert isinstance(display.ax_, mpl.axes.Axes)
    legend = display.ax_.get_legend()
    assert legend.get_title().get_text() == "Test set"
    assert len(legend.get_texts()) == 6 + 1

    assert display.ax_.get_xlabel() == "False Positive Rate"
    assert display.ax_.get_ylabel() == "True Positive Rate"
    assert display.ax_.get_adjustable() == "box"
    assert display.ax_.get_aspect() in ("equal", 1.0)
    assert display.ax_.get_xlim() == display.ax_.get_ylim() == (-0.01, 1.01)
    assert display.ax_.get_title() == "ROC Curve"


def test_binary_classification_kwargs(pyplot, binary_classification_data):
    """Check that we can pass keyword arguments to the ROC curve plot for
    cross-validation."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.roc()
    roc_curve_kwargs = [{"color": "red"}, {"color": "blue"}]
    display.plot(roc_curve_kwargs=roc_curve_kwargs)
    assert display.lines_[0].get_color() == "red"
    assert display.lines_[1].get_color() == "blue"


@pytest.mark.parametrize(
    "fixture_name",
    ["binary_classification_data", "multiclass_classification_data"],
)
@pytest.mark.parametrize("roc_curve_kwargs", [[{"color": "red"}], "unknown"])
def test_multiple_roc_curve_kwargs_error(
    pyplot, fixture_name, request, roc_curve_kwargs
):
    """Check that we raise a proper error message when passing an inappropriate
    value for the `roc_curve_kwargs` argument."""
    estimator, X_train, X_test, y_train, y_test = request.getfixturevalue(fixture_name)

    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.roc()
    err_msg = "You intend to plot multiple curves"
    with pytest.raises(ValueError, match=err_msg):
        display.plot(roc_curve_kwargs=roc_curve_kwargs)


@pytest.mark.parametrize("with_roc_auc", [False, True])
def test_frame_binary_classification(binary_classification_data, with_roc_auc):
    """Test the frame method with binary classification comparison data."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.roc()
    df = display.frame(with_roc_auc=with_roc_auc)

    expected_index = ["estimator_name"]
    expected_columns = ["threshold", "fpr", "tpr"]
    if with_roc_auc:
        expected_columns.append("roc_auc")

    check_frame_structure(df, expected_index, expected_columns)
    assert df["estimator_name"].nunique() == 2

    if with_roc_auc:
        for (_), group in df.groupby(["estimator_name"], observed=True):
            assert group["roc_auc"].nunique() == 1


@pytest.mark.parametrize("with_roc_auc", [False, True])
def test_frame_multiclass_classification(multiclass_classification_data, with_roc_auc):
    """Test the frame method with multiclass classification comparison data."""
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    estimator_2 = clone(estimator).set_params(C=10).fit(X_train, y_train)
    report = ComparisonReport(
        reports={
            "estimator_1": EstimatorReport(
                estimator,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
            "estimator_2": EstimatorReport(
                estimator_2,
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
            ),
        }
    )
    display = report.metrics.roc()
    df = display.frame(with_roc_auc=with_roc_auc)

    expected_index = ["estimator_name", "label"]
    expected_columns = ["threshold", "fpr", "tpr"]
    if with_roc_auc:
        expected_columns.append("roc_auc")

    check_frame_structure(df, expected_index, expected_columns)
    assert df["estimator_name"].nunique() == 2
    assert df["label"].nunique() == len(estimator.classes_)

    if with_roc_auc:
        for (_, _), group in df.groupby(["estimator_name", "label"], observed=True):
            assert group["roc_auc"].nunique() == 1


def test_legend(pyplot, binary_classification_data, multiclass_classification_data):
    """Check the rendering of the legend for ROC curves with a `ComparisonReport`."""

    # binary classification
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.roc()
    display.plot()
    check_legend_position(display.ax_, loc="lower right", position="inside")

    # multiclass classification <= 5 classes
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.roc()
    display.plot()
    check_legend_position(display.ax_, loc="upper left", position="outside")


def test_binary_classification_constructor(binary_classification_data):
    """Check that the dataframe has the correct structure at initialization."""
    estimator, X_train, X_test, y_train, y_test = binary_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.roc()

    index_columns = ["estimator_name", "split_index", "label"]
    for df in [display.roc_curve, display.roc_auc]:
        assert all(col in df.columns for col in index_columns)
        assert df["estimator_name"].unique().tolist() == report.report_names_
        assert df["split_index"].isnull().all()
        assert df["label"].unique() == 1

    assert len(display.roc_auc) == 2


def test_multiclass_classification_constructor(multiclass_classification_data):
    """Check that the dataframe has the correct structure at initialization."""
    estimator, X_train, X_test, y_train, y_test = multiclass_classification_data
    report_1 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report_2 = EstimatorReport(
        estimator, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test
    )
    report = ComparisonReport(
        reports={"estimator_1": report_1, "estimator_2": report_2}
    )
    display = report.metrics.roc()

    index_columns = ["estimator_name", "split_index", "label"]
    for df in [display.roc_curve, display.roc_auc]:
        assert all(col in df.columns for col in index_columns)
        assert df["estimator_name"].unique().tolist() == report.report_names_
        assert df["split_index"].isnull().all()
        np.testing.assert_array_equal(df["label"].unique(), np.unique(y_train))

    assert len(display.roc_auc) == len(np.unique(y_train)) * 2
