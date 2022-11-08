import React from "react";
import validator from "@rjsf/validator-ajv6";
import { Box, Heading } from "@chakra-ui/react";
import { withTheme } from "@rjsf/core";
import { Theme as ChakraUITheme } from "@rjsf/chakra-ui";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useAuth } from "../login/hooks";
import { ApiError } from "../../../casualcms/domain/ports";
import { AppContext } from "../../../config";
import { Draft, PageType } from "../../../casualcms/domain/model";
import { Loader } from "../../components/loader";
import { ApiErrorUI } from "../../components/error_api";
import { PageBreadcrumb } from "../../components/breadcrumb";

const Form = withTheme(ChakraUITheme);

export const PageNew: React.FunctionComponent<{}> = () => {
  // console.log("-------------------------------------------")
  // console.log("# Rendering page new")
  let { pageTypeName } = useParams<string>();
  let auth = useAuth();
  const config = React.useContext(AppContext);
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [pageType, setPageType] = React.useState<PageType | null>(null);
  const [error, setError] = React.useState<ApiError>(null);
  let navigate = useNavigate();
  const [params, setParams] = useSearchParams();

  const parentPath = params.get("parent");
  const [parentPage, setParentPage] = React.useState<Draft | null>(null);

  React.useEffect(() => {
    async function loadPageType() {
      const rtyp = await config.api.pageType.showPageType(
        token,
        pageTypeName || ""
      );
      rtyp
        .map((typ: PageType) => setPageType(typ))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    if (token) {
      loadPageType();
    }
    return () => {
      setIsLoading(true);
      setError(null);
      setPageType(null);
    };
  }, [auth, pageTypeName]);

  React.useEffect(() => {
    async function loadPage() {
      if (parentPath) {
        const page = await config.api.page.showDraft(token, parentPath || "");
        // console.log(page)
        page
          .map((page: Draft) => setParentPage(page))
          .mapErr((err: ApiError) => setError(err));
      } else {
        setParentPage({
          metadata: { path: "", type: "", breadcrumb: { items: [] } },
        });
      }
    }
    loadPage();
    return () => {
      setParentPage(null);
      setError(null);
    };
  }, [parentPath]);

  if (isLoading) {
    return <Loader label="Loading form..." />;
  }
  const onsubmit = async (data: any) => {
    const page = data.formData;
    await config.api.page.createDraft(
      token,
      pageTypeName || "",
      page,
      parentPath
    );
    navigate(`/admin/pages?${params}`, { replace: true });
  };

  const data = {};
  return (
    <Box minW="720px">
      <Heading>New Page</Heading>
      {parentPage && <PageBreadcrumb page={parentPage} title="new page" />}
      <ApiErrorUI error={error} />
      <Box maxW="720px">
        {pageType && (
          <Form
            schema={pageType.schema}
            uiSchema={pageType.uiSchema}
            formData={data}
            validator={validator}
            // onChange={() => console.log("changed")}
            onSubmit={onsubmit}
            // onError={() => console.log("errors")}
          />
        )}
      </Box>
    </Box>
  );
};