import React from "react";
import {
  Box,
  Heading,
  Icon,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { PartialPageTemplate } from "../../casualcms/domain/model";
import { ApiError } from "../../casualcms/domain/ports";
import { AppContext } from "../../config";

import { useAuth } from "../login/components";
import { Link, useSearchParams } from "react-router-dom";
import { ChevronRightIcon } from "@chakra-ui/icons";
import { Loader } from "../loader/components";
import { ApiErrorUI } from "../errorApi/components";

type TemplateTableProps = {
  isLoading: boolean;
  parentPath: string | null;
  templates: PartialPageTemplate[];
};
export const TemplateTable: React.FunctionComponent<TemplateTableProps> = (
  props: TemplateTableProps
) => {
  if (props.isLoading) {
    return <Loader label="loading page templates..." />;
  }

  const templates = props.templates;
  const qs = props.parentPath
    ? new URLSearchParams({ parent: props.parentPath })
    : "";
  return (
    <TableContainer>
      <Table variant="simple">
        <Thead>
          <Tr>
            <Th>Template Type</Th>
          </Tr>
        </Thead>
        <Tbody>
          {templates.map((tpl, i) => (
            <Tr key={i}>
              <Td>
                <Link to={`/admin/page/new/${tpl.type}?${qs}`}>
                  <Icon as={ChevronRightIcon} w={6} h={6} />
                  {tpl.type}
                </Link>
              </Td>
            </Tr>
          ))}
        </Tbody>
      </Table>
    </TableContainer>
  );
};

export const TemplateList: React.FunctionComponent<{}> = () => {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const [isLoading, setIsLoading] = React.useState<boolean>(true);
  const [templates, setTemplates] = React.useState<PartialPageTemplate[]>([]);
  const [error, setError] = React.useState<ApiError>(null);
  const [params, setParams] = useSearchParams();
  const parentType = params.get("type");
  const parentPath = params.get("parent");

  React.useEffect(() => {
    async function loadTemplates() {
      const pageTemplates = await config.api.template.listTemplates(
        token,
        parentType
      );
      pageTemplates
        .map((tpls: PartialPageTemplate[]) => setTemplates(tpls))
        .mapErr((err: ApiError) => setError(err));
      setIsLoading(false);
    }
    loadTemplates();
    return () => {
      setIsLoading(true);
      setError(null);
      setTemplates([]);
    };
  }, []);
  return (
    <Box>
      {
        <>
          <Heading>Choose A Type Of Template</Heading>
          <Box paddingLeft={15}>
            <ApiErrorUI error={error} />
            <TemplateTable
              templates={templates}
              parentPath={parentPath}
              isLoading={isLoading}
            />
          </Box>
        </>
      }
    </Box>
  );
};
